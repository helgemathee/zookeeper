import os
import sys
import datetime
import time
import zookeeper

# redirect output
hook = zookeeper.zkClient.zkSoftimageLogHook(Application)
sys.stdout = hook
sys.stderr = hook

cfg = zookeeper.zkConfig()
scratchdisc_enabled = cfg.get('scratchdisc_enabled', False)
scratchdisc_folder = cfg.get('scratchdisc_folder', '')

def log(message):
  prefix = datetime.datetime.now().strftime("%Y-%m-%d %H::%M::%S: ")
  Application.LogMessage(prefix+message)

def setFrameAsFailed(connection, frame, reason):
  # set to waiting + increase tries
  if frame.tries < 3:
    frame.tries = frame.tries + 1
    frame.status = 'WAITING'
  else:
    frame.status = 'FAILED'
    frame.ended = 'NOW()'
  frame.write()
  log('Frame %d failed: %s' % (frame.time, reason))

def munch():

  connection = zookeeper.zkDB.zkConnection(
    ip = os.environ['ZK_IP'],
    port = int(os.environ['ZK_PORT']),
    database = os.environ['ZK_DATABASE'],
    debug = False
    )

  if not connection.connected:
    log("Cannot establish connection (%s, %s, %s)" % (os.environ['ZK_IP'], os.environ['ZK_PORT'], os.environ['ZK_DATABASE']))
    return

  machine = zookeeper.zkDB.zkMachine.getById(connection, int(os.environ['ZK_MACHINE']))
  project = zookeeper.zkDB.zkProject.getById(connection, int(os.environ['ZK_PROJECT']))
  job = zookeeper.zkDB.zkJob.getById(connection, int(os.environ['ZK_JOB']))
  input = job.input
  frame = zookeeper.zkDB.zkFrame.getById(connection, int(os.environ['ZK_FRAME']))
  scenePath = input.path

  uncMap = zookeeper.zkDB.zkUncMap.getUncMapForMachine(connection, machine.id)

  # localize scene
  if scratchdisc_enabled:
    extFile = zookeeper.zkDB.zkExternalFile.getOrCreateByProjectAndPath(connection, project.id, input.path, type = 'Softimage\\Scenes')
    scratchPath = extFile.getScratchDiskPath(cfg)
    projectFolder = os.path.split(os.path.split(scratchPath)[0])[0]
    Application.ActiveProject2 = Application.CreateProject2(projectFolder)
    scenePath = extFile.synchronize(cfg, uncMap)

  # open scene
  Application.OpenScene(scenePath, False, False)
  scene = Application.ActiveProject.ActiveScene

  # vebosity levels
  # try all of them, add redshift, arnold etc
  try:
    Application.SetValue("Passes.mentalray.VerbosityLevel", 44)
  except:
    pass

  externalFiles = scene.externalFiles
  extFileCompleted = {}
  for i in range(externalFiles.Count):
    xsiFile = externalFiles(i)
    resolvedPath = xsiFile.ResolvedPath
    if extFileCompleted.has_key(resolvedPath):
      xsiFile.Path = extFileCompleted[resolvedPath]
      continue
    extFile = zookeeper.zkDB.zkExternalFile.getOrCreateByProjectAndPath(connection, project.id, resolvedPath, type = xsiFile.FileType)
    scratchPath = extFile.getScratchDiskPath(cfg)
    synchronizedPath = extFile.synchronize(cfg, uncMap)
    extFileCompleted[resolvedPath] = synchronizedPath
    xsiFile.Path = synchronizedPath

  while(True):

    log('Working on %s - %s, frame %d' % (project.name, job.name, frame.time))
    log('Using input "%s"' % input.path)

    frameBuffersToReset = []

    if job.type == 'CAPTURE':
      setFrameAsFailed(connection, frame, 'Job type not supported.')
      pass

    elif job.type == 'ALL':

      # switch pass
      passName = job.name.partition('|')[2]
      try:
        Application.SetCurrentPass("Passes." + passName)
      except:
        setFrameAsFailed(connection, frame, 'Cannot find pass "%s"' % passName)
        break

      # if we are using a scratch disc, please render locally
      if scratchdisc_enabled:
        log('Scratch Disk is enabled, retargeting outputs....')
        Application.SetValue("Passes.RenderOptions.FramePadding", 5) # we always use 5
        currentPass = scene.ActivePass
        frameBuffers = currentPass.FrameBuffers
        for i in range(frameBuffers.Count):
          fb = frameBuffers(i)
          if not fb.Parameters.GetItem('Enabled').Value:
            continue
          output = zookeeper.zkDB.zkOutput.createNew(connection)
          output.frame = frame
          output.name = fb.Name
          output.path = zookeeper.zkClient.zk_uncFromDrivePath(fb.GetResolvedPath(frame.time))
          scratchedPath = output.getScratchFile(cfg, frameToken='[frame]')
          log('Retargeted output from '+fb.FileName.Value+' to '+scratchedPath)
          frameBuffersToReset += [[fb, fb.FileName.Value]]
          fb.FileName.Value = scratchedPath

      # render
      try:
        Application.SetValue("PlayControl.Current", frame.time)
        Application.RenderPasses("Passes." + passName, frame.time, frame.time, 1)
      except:
        setFrameAsFailed(connection, frame, 'Error when launching render')

    # mark the frame as completed
    if not frame.status == 'FAILED':
      if scratchdisc_enabled:
        frame.status = 'COMPLETED'
      else:
        frame.status = 'DELIVERED'
      frame.ended = 'NOW()'
      frame.duration = '(TIMESTAMPDIFF(SECOND, frame_started, NOW()))'

      # add all outputs
      # so that the consumer can move them
      if scratchdisc_enabled:

        # reset so we get the proper resolved paths
        for fb in frameBuffersToReset:
          fb[0].FileName.Value = fb[1]

        currentPass = scene.ActivePass
        frameBuffers = currentPass.FrameBuffers
        for i in range(frameBuffers.Count):
          fb = frameBuffers(i)
          if not fb.Parameters.GetItem('Enabled').Value:
            continue
          output = zookeeper.zkDB.zkOutput.createNew(connection)
          output.frame = frame
          output.name = fb.Name

          frameNormal = str(frame.time)
          framePadded = frameNormal.rjust(5, '0')
          tokens = {
            'Project Path': input.path.replace('/', '\\').partition('\\Scenes\\')[0],
            'Pass': currentPass.Name,
            'FrameBuffer': fb.Name,
            'Padding': framePadded[:5-len(frameNormal)]
          }

          tokenStr = Application.GetValue("Passes.RenderOptions.OutputDir")
          tokenStr += "\\" + fb.FileName.Value + ".[Frame]." + fb.Format.Value
          tokenStr = tokenStr.replace('[Frame]', '[Padding][Frame]')

          projectPath = XSIUtils.ResolveTokenString('[Project Path]', frame.time, True, tokens.keys(), tokens.values())
          tokenStr = XSIUtils.ResolveTokenString(tokenStr, frame.time, True, tokens.keys(), tokens.values())

          if tokenStr.lower().startswith(projectPath.lower()):
            tokenStr = tokens['Project Path'] + tokenStr[len(projectPath):]

          output.path = tokenStr

          frame.pushOutputForSubmit(output)

      frame.write()

    # look for more work
    work = connection.call('look_for_work', [machine.id, 1])
    if len(work) == 0:
      break

    nextFrame = zookeeper.zkDB.zkFrame.getById(connection, id = work[0][0])
    nextJob = nextFrame.job
    nextInput = nextJob.input
    if not nextInput.path == input.path:
      log('Stopping working, next frame uses another input.')
      break

    # when switching jobs, rewind time
    if not nextJob.id == job.id:
      Application.SetValue("PlayControl.Current", Application.GetValue("PlayControl.GlobalIn"))

    nextFrame.machineid = machine.id
    nextFrame.started = 'NOW()'
    nextFrame.status = 'PROCESSING'
    nextFrame.write()

    job = nextJob
    input = nextInput
    frame = nextFrame

munch()

