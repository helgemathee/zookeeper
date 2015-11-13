import os
import re
import psutil
import datetime
import zookeeper
from PySide import QtCore, QtGui

class zkManager(zookeeper.zkUI.zkMainWindow):
  __conn = None
  __cfg = None
  __widgets = None
  __timers = None

  def __init__(self, connection):

    self.__conn = connection
    self.__cfg = zookeeper.zkConfig()

    super(zkManager, self).__init__('Manager')

    self.__widgets = {}
    self.__timers = {}

    self.setMinimumWidth(640)
    self.setMinimumHeight(800)

    self.__widgets['tabs'] = QtGui.QTabWidget()
    self.addWidgetToCentral(self.__widgets['tabs'])

    # jobs
    labels = ['id', 'project', 'job', 'user', 'frames', 'prio', 'status', 'progress']
    self.__widgets['jobs'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_jobs_for_manager',
      labels = labels,
      fillItemCallback = self.onJobFillItem
      )
    self.__widgets['jobs'].contextMenuRequested.connect(self.onJobContextMenu)

    # projects
    labels = ['id', 'project', 'jobs']
    self.__widgets['projects'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_projects_for_manager',
      labels = labels
      )
    self.__widgets['projects'].contextMenuRequested.connect(self.onProjectContextMenu)

    # machines
    labels = ['id', 'name', 'status', 'prio', 'cpu', 'ram']
    self.__widgets['machines'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_machines_for_manager',
      labels = labels,
      fillItemCallback = self.onMachineFillItem
      )
    self.__widgets['machines'].contextMenuRequested.connect(self.onMachineContextMenu)

    # frames
    labels = ['id', 'job', 'time', 'status', 'duration', 'machine', 'prio', 'package']
    self.__widgets['frames'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_frames_for_manager',
      procedureArgs = [0],
      labels = labels,
      fillItemCallback = self.onFrameFillItem
      )
    self.__widgets['frames'].contextMenuRequested.connect(self.onFrameContextMenu)

    # log
    self.__widgets['log'] = QtGui.QPlainTextEdit()

    self.__widgets['tabs'].addTab(self.__widgets['jobs'], 'jobs')
    self.__widgets['tabs'].addTab(self.__widgets['projects'], 'projects')
    self.__widgets['tabs'].addTab(self.__widgets['machines'], 'machines')
    self.__widgets['tabs'].addTab(self.__widgets['frames'], 'frames')
    self.__widgets['tabs'].addTab(self.__widgets['log'], 'log')

    self.__timers['poll'] = QtCore.QTimer(self)
    self.__timers['poll'].setInterval(1000)
    self.__timers['poll'].setSingleShot(False)
    self.connect(self.__timers['poll'], QtCore.SIGNAL("timeout()"), self.poll)

    for key in self.__timers:
      self.__timers[key].start()

    self.show()

  def poll(self):
    widget = self.__widgets['tabs'].currentWidget()
    if hasattr(widget, 'poll'):
      widget.poll()

  def onMachineFillItem(self, table, item, id, caption, data):
    if data is None:
      return False
      
    if caption == 'status':
      if data == 'OFFLINE':
        item.setBackground(QtCore.Qt.red)
      else:
        item.setBackground(QtCore.Qt.green)
    elif caption == 'prio':
      if data == 'OFF':
        item.setBackground(QtCore.Qt.red)
      elif data == 'LOW':
        item.setBackground(QtCore.Qt.yellow)
      elif data == 'MED':
        item.setBackground(QtCore.Qt.green)
      elif data == 'HIGH':
        item.setBackground(QtCore.Qt.darkGreen)
    elif caption == 'cpu':
      s = table.horizontalHeader().sectionSize(4)
      r = int(float(s) * float(data) / 100.0 + 0.5)
      grad = QtGui.QLinearGradient(r-1, 0, r, 0)
      grad.setColorAt(0, QtCore.Qt.blue)
      grad.setColorAt(1, QtCore.Qt.white)
      item.setBackground(grad)
      item.setText(str(data)+'%')
      return True
    elif caption == 'ram':
      s = table.horizontalHeader().sectionSize(5)
      r = int(float(s) * float(data) / 100.0 + 0.5)
      grad = QtGui.QLinearGradient(r-1, 0, r, 0)
      grad.setColorAt(0, QtCore.Qt.magenta)
      grad.setColorAt(1, QtCore.Qt.white)
      item.setBackground(grad)
      item.setText(str(data)+'%')
      return True

    return False

  def onJobFillItem(self, table, item, id, caption, data):
    if data is None:
      return False

    if caption == 'status':
      if data > 0:
        item.setBackground(QtCore.Qt.yellow)
        item.setText('processing')
      else:
        item.setBackground(QtCore.Qt.white)
        item.setText('halted')
      return True
    elif caption == 'progress':
      s = table.horizontalHeader().sectionSize(7)
      r = int(float(s) * float(data) / 100.0 + 0.5)
      grad = QtGui.QLinearGradient(r-1, 0, r, 0)
      grad.setColorAt(0, QtCore.Qt.green)
      grad.setColorAt(1, QtCore.Qt.white)
      item.setBackground(grad)
      item.setText(str(data)+'%')
      return True

    return False

  def onFrameFillItem(self, table, item, id, caption, data):
    if caption == 'status':
      if data == 'PROCESSING':
        item.setBackground(QtCore.Qt.yellow)
      elif data == 'COMPLETED':
        item.setBackground(QtCore.Qt.green)
      elif data == 'DELIVERED':
        item.setBackground(QtCore.Qt.darkGreen)
      elif data == 'STOPPED' or data == 'FAILED':
        item.setBackground(QtCore.Qt.red)
      else:
        item.setBackground(QtCore.Qt.white)
      item.setText(data.lower())
      return True
    elif caption == 'duration':
      if not data:
        item.setText('')
      else:
        seconds = data
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        item.setText("%d:%02d:%02d" % (h, m, s))
      return True
    return False

  def onMachineContextMenu(self, id, col):
    menu = QtGui.QMenu()

    def setupPrioAction(menu, prio):

      def onTriggered():
        self.__conn.call('set_machine_priority', [id, prio])
        self.poll()

      menu.addAction('set %s' % prio).triggered.connect(onTriggered)

    for prio in ['OFF', 'LOW', 'MED', 'HIGH']:
      setupPrioAction(menu, prio)

    pos = QtGui.QCursor().pos()
    menu.exec_(pos)

  def onProjectContextMenu(self, id, col):

    menu = QtGui.QMenu()

    def onNew():
      def onAccepted(fields):
        p = zookeeper.zkDB.zkProject.createNew(self.__conn)
        p.name = fields[0]['value']
        p.write()
        self.poll()

      dialog = zookeeper.zkUI.zkNewProjectDialog(onAccepted, None)
      dialog.exec_()

    menu.addAction('new project').triggered.connect(onNew)

    menu.addSeparator()

    def onDelete():
      msgBox = QtGui.QMessageBox()
      msgBox.setText("Are you sure?")
      msgBox.setInformativeText("This will remove all jobs, frames and outputs...!")
      msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
      msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
      ret = msgBox.exec_()
      if ret == QtGui.QMessageBox.Ok:
        self.__conn.call('delete_project', [id])
        self.poll()
    menu.addAction('delete').triggered.connect(onDelete)

    pos = QtGui.QCursor().pos()
    menu.exec_(pos)

  def onJobContextMenu(self, id, col):

    menu = QtGui.QMenu()

    def onShowFrames():
      self.__widgets['frames'].setProcedureArgs([id])
      self.__widgets['tabs'].setCurrentWidget(self.__widgets['frames'])

    menu.addAction('show frames').triggered.connect(onShowFrames)

    menu.addSeparator()

    def setupPrioAction(menu, prio):

      def onTriggered():
        job = zookeeper.zkDB.zkJob.getById(self.__conn, id)
        job.priority = prio
        job.write()
        self.poll()

      menu.addAction('set prio to %d' % prio).triggered.connect(onTriggered)

    for prio in [25, 50, 57, 100, 125]:
      setupPrioAction(menu, prio)

    menu.addSeparator()

    def onResubmit():
      self.__conn.call('resubmit_job', [id])
      self.poll()
    menu.addAction('resubmit').triggered.connect(onResubmit)

    def onStop():
      self.__conn.call("stop_job", [id])
      self.poll()
    menu.addAction('stop').triggered.connect(onStop)

    def onResume():
      self.__conn.call("resume_job", [id])
      self.poll()
    menu.addAction('resume').triggered.connect(onResume)

    menu.addSeparator()

    def onDelete():
      msgBox = QtGui.QMessageBox()
      msgBox.setText("Are you sure?")
      msgBox.setInformativeText("This will remove all frames and outputs...!")
      msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
      msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
      ret = msgBox.exec_()
      if ret == QtGui.QMessageBox.Ok:
        self.__conn.call('delete_job', [id])
        self.poll()
    menu.addAction('delete').triggered.connect(onDelete)

    pos = QtGui.QCursor().pos()
    menu.exec_(pos)

  def onFrameContextMenu(self, id, col):

    menu = QtGui.QMenu()

    setting = zookeeper.zkDB.zkSetting.getByName(self.__conn, 'log_root')
    if setting:
      def onShowLog():
        frame = zookeeper.zkDB.zkFrame.getById(self.__conn, id)
        path = frame.log
        if path:
          if os.path.exists(path):
            logContent = open(path, "rb").read()
            self.__widgets['log'].setPlainText(logContent)
            self.__widgets['tabs'].setCurrentWidget(self.__widgets['log'])

      menu.addAction('show log').triggered.connect(onShowLog)
      menu.addSeparator()

    def setupPrioAction(menu, prio):

      def onTriggered():
        frame = zookeeper.zkDB.zkFrame.getById(self.__conn, id)
        frame.priority = prio
        frame.write()
        self.poll()

      menu.addAction('set prio to %d' % prio).triggered.connect(onTriggered)

    for prio in [25, 50, 57, 100, 125]:
      setupPrioAction(menu, prio)

    menu.addSeparator()

    def onResubmit():
      self.__conn.call("resubmit_frame", [id])
      self.poll()
    menu.addAction('resubmit').triggered.connect(onResubmit)

    def onStop():
      self.__conn.call("stop_frame", [id])
      self.poll()
    menu.addAction('stop').triggered.connect(onStop)

    def onResume():
      self.__conn.call("resume_frame", [id])
      self.poll()
    menu.addAction('resume').triggered.connect(onResume)

    pos = QtGui.QCursor().pos()
    menu.exec_(pos)
