import os
import datetime
import zookeeper
from PySide import QtCore, QtGui

class zkConsumer(zookeeper.zkUI.zkMainWindow):
  __conn = None
  __machine = None
  __widgets = None
  __timers = None
  __workThread = None

  def __init__(self, connection):

    self.__conn = connection
    self.__machine = zookeeper.zkDB.zkMachine(self.__conn, asClient = True)

    super(zkConsumer, self).__init__('Munch - %s' % self.__machine.name)

    cfg = zookeeper.zkConfig()

    self.__widgets = {}
    self.__timers = {}

    self.setMinimumWidth(640)
    self.setMinimumHeight(800)

    self.__widgets['log'] = QtGui.QPlainTextEdit()
    self.__widgets['log'].setReadOnly(True)
    self.addWidgetToCentral(self.__widgets['log'])

    self.__timers['poll'] = QtCore.QTimer(self)
    self.__timers['poll'].setInterval(cfg.get('clientinterval', 5) * 1000)
    self.__timers['poll'].setSingleShot(False)

    self.connect(self.__timers['poll'], QtCore.SIGNAL("timeout()"), self.poll)

    for key in self.__timers:
      self.__timers[key].start()

    self.show()

  def closeEvent(self, event):
    if self.__workThread:
      self.__workThread.exiting = True
      while self.__workThread.isRunning():
        pass
    super(zkConsumer, self).closeEvent(event)

  def log(self, message):
    prefix = datetime.datetime.now().strftime("%Y-%m-%d %H::%M::%S: ")
    self.__widgets['log'].appendPlainText(prefix+message)

  def poll(self):
    self.__machine.updatePhysicalState()
    
    if self.__workThread:
      if not self.__workThread.isRunning():
        print 'we should check out outputs!'
        print self.__workThread.log
      return

    work = self.__conn.call('look_for_work', [self.__machine.id, 1])
    if len(work) == 0:
      return

    # take the frame
    frame = zookeeper.zkDB.zkFrame.getById(self.__conn, id = work[0][0])
    job = frame.job

    # create the right thread
    self.__workThread = zookeeper.zkClient.zkWorkThread.create(self.__conn, frame, self)
    if self.__workThread:
      self.log('Working on job %s, frame %d' % (job.name, frame.time))
      self.__workThread.start()
