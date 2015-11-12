import os
import sys
import time
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

  def __init__(self, connection, frame, parent = None):
    super(zkWorkThread, self).__init__(parent)
    self.__conn = connection
    self.__frame = frame
    self.__machine = frame.machine
    self.exiting = False

  def __del__(self):
    if self.__process:
      while self.__process.returncode is None:
        self.__process.kill()

  def run(self):
    self.__frame.machineid = self.__machine.id
    self.__frame.started = 'NOW()'
    self.__frame.status = 'PROCESSING'
    self.__frame.write()

  def launchSubProcess(self, cmd, args, env):
    if not os.path.exists(cmd):
      self.__machine.sendNotification('Cannot start "%s"' % cmd, self.frame, severity='ERROR')
      return False

    # ensure to include zookeeper in the path
    zookeeperPath = os.path.split(os.path.split(zookeeper.__file__)[0])[0]
    env['PYTHONPATH'] = env.get('PYTHONPATH') + os.pathsep + zookeeperPath

    # also include all of the zookeeper settings
    env['ZK_IP'] = str(self.connection.ip)
    env['ZK_MACHINE'] = str(self.machine.id)
    env['ZK_FRAME'] = str(self.frame.id)
    env['ZK_JOB'] = str(self.frame.job.id)

    cmdargs = [cmd] + args
    self.__log = []
    self.__process = subprocess.Popen(cmdargs, env = env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  def waitForSubProcess(self):
    while self.exiting==False:
      time.sleep(1)
      out, err = self.__process.communicate()
      out = out.replace('\r', '')
      self.__log += out.split('\n')
      if self.processReturnCode >= 0:
        self.exiting = True

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

  @property
  def machine(self):
    return self.__machine

  @property
  def process(self):
    self.__process

  @property
  def log(self):
    return self.__log

  @classmethod
  def create(self, connection, frame, parent = None):
    job = frame.job

    if job.dcc.lower() == 'softimage':
      return zookeeper.zkClient.zkSoftimageWorkThread(connection, frame, parent)

    return None
