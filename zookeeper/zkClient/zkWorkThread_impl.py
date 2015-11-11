import sys
import time
import zookeeper
from PySide import QtCore, QtGui

class zkWorkThread(QtCore.QThread):

  __conn = None
  __machine = None
  __frame = None

  def __init__(self, connection, frame, parent = None):
    super(zkWorkThread, self).__init__(parent)
    self.__conn = connection
    self.__frame = frame
    self.__machine = frame.machine
    self.exiting = False

  def run(self):
    self.__frame.machineid = self.__machine.id
    self.__frame.started = 'NOW()'
    self.__frame.status = 'PROCESSING'
    self.__frame.write()

  @property
  def connection(self):
    return self.__conn

  @property
  def frame(self):
    return self.__frame

  @property
  def machine(self):
    return self.__machine

  @classmethod
  def create(self, connection, frame, parent = None):
    job = frame.job

    if job.dcc.lower() == 'softimage':
      return zookeeper.zkClient.zkSoftimageWorkThread(connection, frame, parent)

    return None
