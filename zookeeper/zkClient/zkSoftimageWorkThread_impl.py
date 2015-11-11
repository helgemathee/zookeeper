import sys
import time
import zookeeper
from PySide import QtCore, QtGui

from zkWorkThread_impl import zkWorkThread

class zkSoftimageWorkThread(zkWorkThread):

  def __init__(self, connection, frame, parent = None):
    super(zkSoftimageWorkThread, self).__init__(connection, frame, parent)

  def run(self):
    super(zkSoftimageWorkThread, self).run()

    while self.exiting==False:
      sys.stdout.write('.')
      sys.stdout.flush()
      time.sleep(1)    

