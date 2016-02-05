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
  Application.LogMessage(prefix+str(message))

def setFrameAsFailed(connection, frame, reason):
  frame.setAsFailed()
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
  jobMachine = zookeeper.zkDB.zkMachine.getById(connection, job.machine)
  input = job.input
  frame = zookeeper.zkDB.zkFrame.getById(connection, int(os.environ['ZK_FRAME']))
  scenePath = input.path

  uncMap = zookeeper.zkDB.zkUncMap.getUncMapForMachine(connection, jobMachine.id)

  # localize scene
  if scratchdisc_enabled:
    extFile = zookeeper.zkDB.zkExternalFile.getOrCreateByProjectAndPaths(connection, project.id, input.path, input.path, type = 'Softimage\\Scenes')
    scratchPath = extFile.getScratchDiskPath(cfg)
    projectFolder = os.path.split(os.path.split(scratchPath)[0])[0]
    Application.ActiveProject2 = Application.CreateProject2(projectFolder)
    scenePath = extFile.synchronize(cfg, uncMap)

  scnTocPath = input.path + 'toc'
  modelResolution = {}
  if os.path.exists(scnTocPath):
    scnTocContent = open(scnTocPath, 'r').read().split('\n')
    for line in scnTocContent:
      l = line.strip()
      if not l.startswith('<Model name='):
        continue
      if l.find('active_resolution') == -1:
        continue
      l = l[13:]
      (modelName, sep, l) = l.partition('"')
      l = l.strip()
      l = l.partition('"')[2]
      res = int(l.partition('"')[0])
      modelResolution[str(modelName)] = res
      log("Referenced model %s is using resolution %d in scntoc file." % (str(modelName), res))

  # open scene
  Application.OpenScene(scenePath, False, False)
  scene = Application.ActiveProject.ActiveScene
  sceneRoot = Application.ActiveSceneRoot

  # redirect the scene output if it is using the [Scene] token
  sceneName = os.path.split(input.path)[1].rpartition('.')[0]
  outputDir = Application.GetValue('Passes.RenderOptions.OutputDir')
  outputDir = str(outputDir).replace('[Scene]', sceneName)
  Application.SetValue('Passes.RenderOptions.OutputDir', outputDir)

  # vebosity levels
  # try all of them, add redshift, arnold etc
  settings = [
    ["Passes.mentalray.VerbosityLevel", 44],
    ["Passes.Redshift_Options.LogLevel", 2],
    # ["Passes.Redshift_Options.AbortOnLicenseFail", True]
    ]
  for setting in settings:
    try:
      Application.SetValue(setting[0], setting[1])
      log("Set '%s' to '%s'" % (setting[0], str(setting[1])))
    except:
      pass

  # remember all model resolutions
  models = sceneRoot.Models
  for i in range(models.Count):
    model = models(i)
    if model.ModelKind != 1:
      continue
    if modelResolution.has_key(str(model.name)):
      continue
    res = int(model.active_resolution.value)
    modelResolution[str(model.name)] = res
    log("Referenced model %s is using resolution %d." % (str(model.name), res))

  xsiFiles = scene.ExternalFiles
  extFileCompleted = {}
  for i in range(xsiFiles.Count):
    xsiFile = xsiFiles(i)
    if xsiFile.FileType != 'Models':
      continue 
  
    resolvedPath = xsiFile.ResolvedPath
    userPath = xsiFile.Path
  
    extFile = zookeeper.zkDB.zkExternalFile.getByProjectAndUserPath(connection, project.id, userPath)
    if not extFileCompleted.has_key(userPath) and extFile:
      log('Found external file for "%s"' % userPath)
      synchronizedPath = extFile.synchronize(cfg, uncMap)
      if not synchronizedPath:
        log('ERROR: Could not synchronize file.')
        continue
      else:
        extFileCompleted[userPath] = synchronizedPath
        xsiFile.Path = synchronizedPath
    elif not extFile:
      log("ERROR: External file for \"%s\" not found in DB!" % userPath)
      continue
    else:
      xsiFile.Path = extFileCompleted[userPath]

  for modelName in modelResolution:
    log("Hit referenced model %s" % (modelName))
    res = modelResolution[modelName]
    activeRes = Application.GetValue('%s.active_resolution' % modelName)
    Application.UpdateReferencedModel(modelName)
    if activeRes != res:
      Application.SetValue('%s.active_resolution' % modelName, res)
      model.active_resolution.value = res
    if res == 0:
      log('Skipping offloaded ref model %s' % (modelName))
    Application.MakeModelLocal(modelName, "", "")

  xsiFiles = scene.ExternalFiles
  for i in range(xsiFiles.Count):
    xsiFile = xsiFiles(i)
    if xsiFile.FileType == 'Models':
      continue 

    resolvedPath = xsiFile.ResolvedPath

    # invalid rigid body cache
    if resolvedPath.lower().endswith('rigidbodycache.xsi'):
      continue

    userPath = xsiFile.Path
    if extFileCompleted.has_key(userPath):
      xsiFile.Path = extFileCompleted[userPath]
      continue
  
    extFile = zookeeper.zkDB.zkExternalFile.getByProjectAndUserPath(connection, project.id, userPath)
    if extFile:
      log('Found external file for "%s"' % userPath)
      synchronizedPath = extFile.synchronize(cfg, uncMap)
      if not synchronizedPath:
        log('ERROR: Could not synchronize file.')
        continue
      else:
        extFileCompleted[userPath] = synchronizedPath
        xsiFile.Path = synchronizedPath
    else:
      log("ERROR: External file for \"%s\" not found in DB!" % userPath)
      continue

  # redshift IES profile files
  objects = Application.FindObjects('', '{6495C5C1-FD18-474E-9703-AEA66631F7A7}')
  for i in range(objects.Count):
    o = objects(i)
    if not o.Name.lower() == 'redshift_ies':
      continue
    userPath = str(o.profileString.Value)
    if extFileCompleted.has_key(userPath):
      Application.SetValue(str(o.profileString), str(extFileCompleted[userPath]))
      continue

    extFile = zookeeper.zkDB.zkExternalFile.getByProjectAndUserPath(connection, project.id, userPath)
    if extFile:
      log('Found external file for "%s"' % userPath)
      synchronizedPath = extFile.synchronize(cfg, uncMap)
      if not synchronizedPath:
        log('ERROR: Could not synchronize file.')
        continue
      else:
        extFileCompleted[userPath] = synchronizedPath
        Application.SetValue(str(o.profileString), str(extFileCompleted[userPath]))
    else:
      log("ERROR: External file for \"%s\" not found in DB!" % userPath)
      continue

  scenePathParts = scenePath.rpartition('.')
  scenePathChanged = scenePathParts[0] + '_resolved' + scenePathParts[1] + scenePathParts[2]
  Application.SaveSceneAs(scenePathChanged)
  Application.OpenScene(scenePathChanged, False, False)
  scene = Application.ActiveProject.ActiveScene

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

          # replace the scene token with the original scene name
          # this might have changed due to scratch disc file name
          # which are different than the original file names.
          fn = str(fb.FileName.Value).replace('[Scene]', sceneName)
          fb.FileName.Value = fn

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

        if scratchdisc_enabled:
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
        else:
          output.path = fb.GetResolvedPath(frame.time)
          output.status = 'DELIVERED'

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

    nextFrame.setAsProcessing(machine.id)

    job = nextJob
    input = nextInput
    frame = nextFrame

munch()

