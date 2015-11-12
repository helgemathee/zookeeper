import os
import datetime
import time
import zookeeper

def log(message):
  prefix = datetime.datetime.now().strftime("%Y-%m-%d %H::%M::%S: ")
  Application.LogMessage(prefix+message)

def setFrameAsFailed(connection, frame, reason):
  # set to waiting + increase tries
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

  # open scene
  Application.OpenScene(input.path, False, False)

  # vebosity levels
  # try all of them, add redshift, arnold etc
  try:
    Application.SetValue("Passes.mentalray.VerbosityLevel", 44)
  except:
    pass

  # todo: localize all external files

  while(True):

    log('Working on %s - %s, frame %d' % (project.name, job.name, frame.time))
    log('Using input "%s"' % input.path)

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

      # todo: localize all output files

      # render
      try:
        Application.RenderPasses("Passes." + passName, frame.time, frame.time, 1)
      except:
        setFrameAsFailed(connection, frame, 'Error when launching render')

    # mark the frame as completed
    if not frame.status == 'FAILED':
      frame.status = 'COMPLETED'
      frame.ended = 'NOW()'
      frame.duration = '(TIMESTAMPDIFF(SECOND, frame_started, NOW()))'
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

    nextFrame.machineid = machine.id
    nextFrame.started = 'NOW()'
    nextFrame.status = 'PROCESSING'
    nextFrame.write()

    job = nextJob
    input = nextInput
    frame = nextFrame

munch()

