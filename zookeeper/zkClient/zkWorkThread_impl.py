import os
import sys
import time
import psutil
import tempfile
import subprocess
import zookeeper
from PySide import QtCore, QtGui

class zkWorkThread(QtCore.QThread):

  __conn = None
  __machine = None
  __frame = None
  __process = None
  __log = None

  logged = QtCore.Signal(str)

  def __init__(self, connection, frame, parent = None):
    super(zkWorkThread, self).__init__(parent)
    self.__conn = connection
    self.__frame = frame
    self.__machine = frame.machine
    self.exiting = False
    self.setTerminationEnabled(True)
    self.__log = []

  def __del__(self):
    if self.__process:
      while self.__process.returncode is None:
        self.__process.kill()

  def run(self):
    self.__frame.setAsProcessing(self.__machine.id)

  def launchSubProcess(self, cmd, args, env):

    if not os.path.exists(cmd):
      self.__machine.sendNotification('Cannot start "%s"' % cmd, self.frame, severity='ERROR')
      return False

    # ensure to include zookeeper in the path
    zookeeperPath = os.path.split(os.path.split(zookeeper.__file__)[0])[0]
    env['PYTHONPATH'] = env.get('PYTHONPATH') + os.pathsep + zookeeperPath

    cfg = zookeeper.zkConfig()
    job = self.frame.job
    project = self.frame.project

    # also include all of the zookeeper settings
    env['ZK_IP'] = self.connection.ip
    env['ZK_PORT'] = self.connection.port
    env['ZK_DATABASE'] = self.connection.database
    env['ZK_MACHINE'] = self.machine.id
    env['ZK_PROJECT'] = self.frame.projectid
    env['ZK_PROJECT_SCRATCH_FOLDER'] = project.getScratchFolder(cfg)
    env['ZK_JOB'] = self.frame.jobid
    env['ZK_JOB_SCRATCH_FOLDER'] = job.getScratchFolder(cfg)
    env['ZK_FRAME'] = self.frame.id
    env['ZK_DCC'] = job.dcc
    env['ZK_DCC_VERSION'] = job.dccversion
    env['ZK_RENDERER'] = job.renderer
    env['ZK_RENDERER_VERSION'] = job.rendererversion

    # fill in all config fields as env vars
    cfgFields = cfg.getFields()
    for f in cfgFields:
      env['ZK_' + str(f['name'].upper())] = str(f['value'])

    for key in env:
      env[key] = str(env[key])

    cmdargs = [cmd] + args
    self.__process = subprocess.Popen(cmdargs, env = env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = False)

    p = psutil.Process(self.__process.pid)
    if self.__machine.priority == 'LOW':
      p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    elif self.__machine.priority == 'MED':
      p.nice(psutil.NORMAL_PRIORITY_CLASS)
    elif self.__machine.priority == 'HIGH':
      p.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)


  def waitForSubProcess(self):
    while self.exiting == False:
      for line in iter(self.__process.stdout.readline, b''):
        l = line.replace('\n', '')
        self.log(l)
        break
      if self.processReturnCode >= 0:
        self.exiting = True

    if self.__process.returncode is None:
      self.log('Killing process...')
      while self.__process.returncode is None:
        self.__process.kill()

  @property
  def processReturnCode(self):
    if self.__process is None:
      return -1
    self.__process.poll()
    return self.__process.returncode

  @property
  def connection(self):
    return self.__conn

  @property
  def frame(self):
    return self.__frame

  def setFrame(self, frame):
    self.__frame = frame

  @property
  def machine(self):
    return self.__machine

  @property
  def process(self):
    self.__process

  def log(self, message):
    self.__log.append(message)
    self.logged.emit(message)

  def logCallback(self, **args):
    message = args.get('message', '')
    if not message:
      return
    self.log(message)

  def clearLog(self):
    log = self.__log
    self.__log = []
    return log

  @classmethod
  def create(self, connection, frame, parent = None):
    job = frame.job

    if job.dcc.lower() == 'softimage':
      return zookeeper.zkClient.zkSoftimageWorkThread(connection, frame, parent)

    return None
