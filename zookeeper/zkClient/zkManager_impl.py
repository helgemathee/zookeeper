import os
import re
import psutil
import time
import datetime
import zookeeper
import subprocess
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

    self.__widgets['buttonsWidget'] = QtGui.QWidget()
    self.__widgets['buttonsWidget'].setContentsMargins(0, 0, 0, 0)
    self.addWidgetToCentral(self.__widgets['buttonsWidget'])

    buttonsLayout = QtGui.QHBoxLayout()
    self.__widgets['buttonsWidget'].setLayout(buttonsLayout)

    self.__widgets['refreshButton'] = QtGui.QPushButton("Refresh", self.__widgets['buttonsWidget'])
    buttonsLayout.addWidget(self.__widgets['refreshButton'])
    self.__widgets['refreshButton'].clicked.connect(self.poll)

    self.__widgets['tabs'] = QtGui.QTabWidget()
    self.addWidgetToCentral(self.__widgets['tabs'])

    # jobs
    labels = ['project', 'job', 'user', 'frames', 'prio', 'status', 'progress']
    self.__widgets['jobs'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_jobs_for_manager',
      labels = labels,
      getItemDataCallback = self.onJobGetData
      )
    self.__widgets['jobs'].contextMenuRequested.connect(self.onJobContextMenu)
    self.__widgets['jobs'].doubleClicked.connect(self.onJobDoubleClicked)

    # projects
    labels = ['project', 'jobs']
    self.__widgets['projects'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_projects_for_manager',
      labels = labels
      )
    self.__widgets['projects'].contextMenuRequested.connect(self.onProjectContextMenu)

    # machines
    labels = ['name', 'status', 'prio', 'cpu', 'ram']
    self.__widgets['machines'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_machines_for_manager',
      labels = labels,
      getItemDataCallback = self.onMachineGetData
      )
    self.__widgets['machines'].contextMenuRequested.connect(self.onMachineContextMenu)

    # frames
    labels = ['job', 'time', 'status', 'duration', 'machine', 'prio', 'package']
    self.__widgets['frames'] = zookeeper.zkUI.zkDbTable(
      self.__conn,
      zookeeper.zkDB.zkMachine,
      procedure = 'get_frames_for_manager',
      procedureArgs = [0],
      labels = labels,
      getItemDataCallback = self.onFrameGetData
      )
    self.__widgets['frames'].contextMenuRequested.connect(self.onFrameContextMenu)
    self.__widgets['frames'].doubleClicked.connect(self.onFrameDoubleClicked)

    # log
    self.__widgets['log'] = QtGui.QPlainTextEdit()

    self.__widgets['tabs'].addTab(self.__widgets['jobs'], 'jobs')
    self.__widgets['tabs'].addTab(self.__widgets['projects'], 'projects')
    self.__widgets['tabs'].addTab(self.__widgets['machines'], 'machines')
    self.__widgets['tabs'].addTab(self.__widgets['frames'], 'frames')
    self.__widgets['tabs'].addTab(self.__widgets['log'], 'log')

    self.__timers['poll'] = QtCore.QTimer(self)
    self.__timers['poll'].setInterval(5000)
    self.__timers['poll'].setSingleShot(False)
    self.connect(self.__timers['poll'], QtCore.SIGNAL("timeout()"), self.poll)

    for key in self.__timers:
      self.__timers[key].start()

    self.show()

  def poll(self):
    widget = self.__widgets['tabs'].currentWidget()
    if hasattr(widget, 'pollOnModel'):
      widget.pollOnModel()

  def onMachineGetData(self, table, caption, id, data, role):
    if data is None:
      return None
      
    if caption == 'status':
      if role == QtCore.Qt.BackgroundRole:
        if data == 'OFFLINE':
          return QtGui.QBrush(QtCore.Qt.red)
        else:
          return QtGui.QBrush(QtCore.Qt.green)
    elif caption == 'prio':
      if role == QtCore.Qt.BackgroundRole:
        if data == 'OFF':
          return QtGui.QBrush(QtCore.Qt.red)
        elif data == 'LOW':
          return QtGui.QBrush(QtCore.Qt.yellow)
        elif data == 'MED':
          return QtGui.QBrush(QtCore.Qt.green)
        elif data == 'HIGH':
          return QtGui.QBrush(QtCore.Qt.darkGreen)

    elif caption == 'cpu':
      if role == QtCore.Qt.DisplayRole:
        return str(data) + '%'
      elif role == QtCore.Qt.BackgroundRole:
        s = table.horizontalHeader().sectionSize(3)
        r = int(float(s) * float(data) / 100.0 + 0.5)
        grad = QtGui.QLinearGradient(r-1, 0, r, 0)
        grad.setColorAt(0, QtCore.Qt.blue)
        grad.setColorAt(1, QtCore.Qt.white)
        return QtGui.QBrush(grad)

    elif caption == 'ram':
      if role == QtCore.Qt.DisplayRole:
        return str(data) + '%'
      elif role == QtCore.Qt.BackgroundRole:
        s = table.horizontalHeader().sectionSize(4)
        r = int(float(s) * float(data) / 100.0 + 0.5)
        grad = QtGui.QLinearGradient(r-1, 0, r, 0)
        grad.setColorAt(0, QtCore.Qt.magenta)
        grad.setColorAt(1, QtCore.Qt.white)
        return QtGui.QBrush(grad)

    return data

  def onJobGetData(self, table, caption, id, data, role):
    if data is None:
      return None

    if caption == 'status':
      if role == QtCore.Qt.DisplayRole:
        if data > 0:
          return 'processing'
        else:
          return 'halted'
      elif role == QtCore.Qt.BackgroundRole:
        if data > 0:
          return QtGui.QBrush(QtCore.Qt.yellow)
        else:
          return None

    elif caption == 'progress':
      if role == QtCore.Qt.DisplayRole:
        return str(data)+'%'
      elif role == QtCore.Qt.BackgroundRole:
        s = table.horizontalHeader().sectionSize(6)
        r = int(float(s) * float(data) / 100.0 + 0.5)
        grad = QtGui.QLinearGradient(r-1, 0, r, 0)
        grad.setColorAt(0, QtCore.Qt.green)
        grad.setColorAt(1, QtCore.Qt.white)
        return QtGui.QBrush(grad)

    return data

  def onFrameGetData(self, table, caption, id, data, role):
    if caption == 'status':
      if role == QtCore.Qt.DisplayRole:
        return data.lower()
      elif role == QtCore.Qt.BackgroundRole:
        if data == 'PROCESSING':
          return QtGui.QBrush(QtCore.Qt.yellow)
        elif data == 'COMPLETED':
          return QtGui.QBrush(QtCore.Qt.green)
        elif data == 'DELIVERED':
          return QtGui.QBrush(QtCore.Qt.darkGreen)
        elif data == 'STOPPED' or data == 'FAILED':
          return QtGui.QBrush(QtCore.Qt.red)

    elif caption == 'duration':
      if role == QtCore.Qt.DisplayRole:
        if data: 
          seconds = data
          m, s = divmod(seconds, 60)
          h, m = divmod(m, 60)
          return "%d:%02d:%02d" % (h, m, s)

    return data

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

  def launchFlipBook(self, job_id, output_name):
    frame_range = self.__conn.call('get_frame_range_for_job', [job_id])
    output = zookeeper.zkDB.zkOutput.getByCondition(self.__conn, 'output_jobid = %s AND output_name = %s' % (job_id, repr(str(output_name))))
    path = self.getResolvedPathFromJob(output.job, output.path)

    mainParts = os.path.split(path)
    fileParts = mainParts[1].split('.')
    file_ext = fileParts[-1]
    frame_no = fileParts[-2]

    path = mainParts[0]
    for i in range(len(fileParts)-2):
      path = os.path.join(path, fileParts[i])
    path += '.'+file_ext

    softimage_root_folder = self.__cfg.get('softimage_root_folder', '')
    dccVersion = self.__cfg.get('softimage_flipbook_version', '2014 SP2')

    env = zookeeper.zkClient.getSoftimageEnv(self.__cfg, '2014 SP2')
    for key in env:
      env[key] = str(env[key])

    bin = os.path.join(softimage_root_folder, 'Softimage '+dccVersion, 'Application', 'bin', 'flip.exe')
    padding = '(fn).%s(ext)' % ''.ljust(len(frame_no), '#')
    cmdArgs = [bin, path, frame_range[0][0], frame_range[0][1], 1, 30, '-p', padding, '-m']

    for i in range(len(cmdArgs)):
      cmdArgs[i] = str(cmdArgs[i])
    subprocess.Popen(cmdArgs, env = env)

  def _setupFlipbookAction(self, menu, job_id, output_name):

    def onTriggered():
      self.launchFlipBook(job_id, output_name)

    menu.addAction('open %s in flipbook' % output_name).triggered.connect(onTriggered)

  def onJobContextMenu(self, id, col):

    menu = QtGui.QMenu()

    def setupRevealAction(menu, job_id, output_name):

      def onTriggered():
        output = zookeeper.zkDB.zkOutput.getByCondition(self.__conn, 'output_jobid = %s AND output_name = %s' % (job_id, repr(str(output_name))))
        filePath = self.getResolvedPathFromJob(output.job, output.path)
        filePath = os.path.split(filePath)[0]
        url = QtCore.QUrl()
        if filePath.startswith("\\\\") or filePath.startswith("//"):
          url.setUrl(QtCore.QDir.toNativeSeparators(filePath))
        else:
          url = QtCore.QUrl.fromLocalFile(filePath);
        QtGui.QDesktopServices.openUrl(url)

      menu.addAction('open %s folder' % output_name).triggered.connect(onTriggered)

    outputs = self.__conn.call('get_outputs_per_job', [id])
    if len(outputs) > 0:
      for output in outputs:
        setupRevealAction(menu, id, output[0])
      menu.addSeparator()
      for output in outputs:
        self._setupFlipbookAction(menu, id, output[0])
      menu.addSeparator()

    def onShowFrames():
      self.__widgets['frames'].model().setProcedureArgs([id])
      self.__widgets['tabs'].setCurrentWidget(self.__widgets['frames'])

    menu.addAction('show frames in manager').triggered.connect(onShowFrames)

    menu.addSeparator()
    def setupPrioAction(menu, prio):

      def onTriggered():
        job = zookeeper.zkDB.zkJob.getById(self.__conn, id)
        job.priority = prio
        job.write()
        self.poll()

      menu.addAction('set prio to %d' % prio).triggered.connect(onTriggered)

    for prio in [25, 50, 75, 100, 125]:
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

  def onJobDoubleClicked(self, index):
    id = self.__widgets['jobs'].model().getIdFromIndex(index)
    self.__widgets['frames'].model().setProcedureArgs([id])
    self.__widgets['tabs'].setCurrentWidget(self.__widgets['frames'])

  def onFrameContextMenu(self, id, col):

    menu = QtGui.QMenu()

    def setupRevealAction(menu, output_id, output_name, asFolder = False):

      def onTriggered():
        output = zookeeper.zkDB.zkOutput.getById(self.__conn, output_id)
        filePath = self.getResolvedPathFromJob(output.job, output.path)
        if asFolder:
          filePath = os.path.split(filePath)[0]
        url = QtCore.QUrl()
        if filePath.startswith("\\\\") or filePath.startswith("//"):
          url.setUrl(QtCore.QDir.toNativeSeparators(filePath))
        else:
          url = QtCore.QUrl.fromLocalFile(filePath);
        QtGui.QDesktopServices.openUrl(url)

      menu.addAction('open %s%s' % (output_name, (' folder' if asFolder else ''))).triggered.connect(onTriggered)

    outputs = self.__conn.call('get_outputs_per_frame', [id])
    if len(outputs) > 0:
      for output in outputs:
        setupRevealAction(menu, output[0], output[1])
      menu.addSeparator()
      for output in outputs:
        setupRevealAction(menu, output[0], output[1], True)
      menu.addSeparator()
      frame = zookeeper.zkDB.zkFrame.getById(self.__conn, id)
      for output in outputs:
        self._setupFlipbookAction(menu, frame.jobid, output[1])
      menu.addSeparator()

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

    for prio in [25, 50, 75, 100, 125]:
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

  def onFrameDoubleClicked(self, index):
    id = self.__widgets['frames'].model().getIdFromIndex(index)
    frame = zookeeper.zkDB.zkFrame.getById(self.__conn, id)
    outputs = frame.getAllOutputs()
    if len(outputs) > 0:
      filePath = outputs[0].path
      filepath = self.getResolvedPathFromJob(frame.job, filePath)

      url = QtCore.QUrl()
      if filePath.startswith("\\\\") or filePath.startswith("//"):
        url.setUrl(QtCore.QDir.toNativeSeparators(filePath))
      else:
        url = QtCore.QUrl.fromLocalFile(filePath);
      QtGui.QDesktopServices.openUrl(url)

  def getResolvedPathFromJob(self, job, path):
    uncmap = zookeeper.zkDB.zkUncMap.getUncMapForMachine(self.__conn, job.machine)
    for drive in uncmap:
      if path.lower().startswith(drive.lower()):
        path = uncmap[drive] + path[len(drive):]
    return path
