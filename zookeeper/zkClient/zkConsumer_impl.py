import os
import re
import psutil
import shutil
import datetime
import zookeeper
from PySide import QtCore, QtGui

class zkConsumer(zookeeper.zkUI.zkMainWindow):
  __conn = None
  __cfg = None
  __machine = None
  __widgets = None
  __timers = None
  __workThread = None
  __percEx = None

  def __init__(self, connection):

    self.__percEx = re.compile(r'.*[^0-9\.]([0-9\.]+%)[^0-9\.]*')
    self.__conn = connection
    self.__machine = zookeeper.zkDB.zkMachine(self.__conn, asClient = True)

    super(zkConsumer, self).__init__('Munch - %s' % self.__machine.name)

    if not os.environ['USERNAME'].lower() == 'render':
      QtGui.QMessageBox.critical(None, "ZooKeeper Error", 'You need to be logged on as the render user.')
      self.close()
      return

    (networkSuccess, networkError) = zookeeper.zkClient.zk_mapAllValidNetworkShares(connection, deleteExisting=True)
    if not networkSuccess:
      QtGui.QMessageBox.critical(None, "ZooKeeper Error", networkError)
      self.close()
      return

    self.__cfg = zookeeper.zkConfig()

    self.__widgets = {}
    self.__timers = {}

    self.setMinimumWidth(640)
    self.setMinimumHeight(800)

    topWidget = QtGui.QWidget()
    topWidget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
    topLayout = QtGui.QGridLayout()
    topWidget.setLayout(topLayout)
    self.addWidgetToCentral(topWidget)

    offset = 0

    backgroundColor = '#e6e6e6'

    # project
    labelWidget = QtGui.QLabel('project', topWidget)
    self.__widgets['project'] = QtGui.QLineEdit(topWidget)
    self.__widgets['project'].setReadOnly(True)
    self.setLineEditColor('project', backgroundColor)
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['project'], 1, offset)
    offset = offset + 1

    # job
    labelWidget = QtGui.QLabel('job', topWidget)
    self.__widgets['job'] = QtGui.QLineEdit(topWidget)
    self.__widgets['job'].setReadOnly(True)
    self.setLineEditColor('job', backgroundColor)
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['job'], 1, offset)
    offset = offset + 1

    # frame
    labelWidget = QtGui.QLabel('frame', topWidget)
    self.__widgets['frame'] = QtGui.QLineEdit(topWidget)
    self.__widgets['frame'].setReadOnly(True)
    self.__widgets['frame'].setMaximumWidth(50)
    self.setLineEditColor('frame', backgroundColor)
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['frame'], 1, offset)
    offset = offset + 1

    # progress
    labelWidget = QtGui.QLabel('progress', topWidget)
    self.__widgets['progress'] = QtGui.QProgressBar(topWidget)
    self.__widgets['progress'].setMinimumWidth(200)
    self.setProgressBarColor('progress', 'green')
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['progress'], 1, offset)
    offset = offset + 1

    # status
    labelWidget = QtGui.QLabel('status', topWidget)
    self.__widgets['status'] = QtGui.QLineEdit('idle', topWidget)
    self.__widgets['status'].setReadOnly(True)
    self.__widgets['status'].setMaximumWidth(75)
    self.__widgets['status'].setAlignment(QtCore.Qt.AlignHCenter)
    if self.__machine.priority == 'OFF':
      self.__widgets['status'].setText('off')
      self.setLineEditColor('status', 'red')
    else:
      self.setLineEditColor('status', 'yellow')
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['status'], 1, offset)
    offset = offset + 1

    # cpu
    labelWidget = QtGui.QLabel('cpu', topWidget)
    self.__widgets['cpu'] = QtGui.QProgressBar(topWidget)
    self.setProgressBarColor('cpu', 'blue')
    self.__widgets['cpu'].setMaximumWidth(60)
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['cpu'], 1, offset)
    offset = offset + 1

    # ram
    labelWidget = QtGui.QLabel('ram', topWidget)
    self.__widgets['ram'] = QtGui.QProgressBar(topWidget)
    self.setProgressBarColor('ram', 'violet')
    self.__widgets['ram'].setMaximumWidth(60)
    topLayout.addWidget(labelWidget, 0, offset)
    topLayout.addWidget(self.__widgets['ram'], 1, offset)
    offset = offset + 1

    self.__widgets['log'] = QtGui.QPlainTextEdit()
    self.__widgets['log'].setReadOnly(True)
    self.addWidgetToCentral(self.__widgets['log'])

    self.__timers['poll'] = QtCore.QTimer(self)
    self.__timers['poll'].setInterval(5003) # every 5 seconds
    self.__timers['poll'].setSingleShot(False)

    self.__timers['garbagecollect'] = QtCore.QTimer(self)
    self.__timers['garbagecollect'].setInterval(15 * 60 * 1000) # every 15 minutes
    self.__timers['garbagecollect'].setSingleShot(False)

    self.__timers['delivery'] = QtCore.QTimer(self)
    self.__timers['delivery'].setInterval(15107) # every 15 seconds, not quite so we don't overlap
    self.__timers['delivery'].setSingleShot(False)

    self.connect(self.__timers['poll'], QtCore.SIGNAL("timeout()"), self.poll)
    self.connect(self.__timers['delivery'], QtCore.SIGNAL("timeout()"), self.delivery)
    self.connect(self.__timers['garbagecollect'], QtCore.SIGNAL("timeout()"), self.garbagecollect)

    for key in self.__timers:
      self.__timers[key].start()

    self.show()
    self.garbagecollect()

  def setLineEditColor(self, name, background):
    style = "QLineEdit { background-color: %s }" % (background)
    self.__widgets[name].setStyleSheet(style)

  def setProgressBarColor(self, name, color):
    style = """
    QProgressBar{
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: %s;
    }
    """ % (color)
    self.__widgets[name].setStyleSheet(style)

  def closeEvent(self, event):
    if self.__workThread:
      self.__workThread.exiting = True
      while self.__workThread.isRunning():
        pass
    super(zkConsumer, self).closeEvent(event)

  # @QtCore.Slot(str)
  def onLogged(self, message):
    message = message.replace('\n', '')
    message = message.replace('\r', '')

    match = self.__percEx.match(message)
    if match:
      self.__widgets['progress'].setValue(float(match.group(1)[:-1]))
    self.__widgets['log'].appendPlainText(message)
    print message

  def log(self, message):
    prefix = datetime.datetime.now().strftime("%Y-%m-%d %H::%M::%S: ")
    self.__widgets['log'].appendPlainText(prefix+message)
    print message

  def storeLog(self, frame):
    log = self.__workThread.clearLog()
    path = frame.getLogFilePath()
    if path and log:
      open(path, "wb").write('\n'.join(log))
      frame.log = path
      frame.write()
    self.__widgets['log'].clear()

  def poll(self):
    self.__machine.updatePhysicalState()
    self.__machine.read()
    priority = self.__machine.priority

    self.__widgets['cpu'].setValue(self.__machine.cpuusage)
    self.__widgets['ram'].setValue(int(100.0 * float(self.__machine.ramusedmb) / float(self.__machine.ramgb * 1024) + 0.5))

    if self.__workThread:

      # if we are running, but priority is off now
      if priority == 'OFF':
        self.__workThread.exiting = True
        self.__workThread = None
        self.__widgets['status'].setText('off')
        self.setLineEditColor('status', 'red')
        self.__widgets['project'].setText('')
        self.__widgets['job'].setText('')
        self.__widgets['frame'].setText('')
        self.__widgets['progress'].setValue(0)
        # self.__widgets['log'].clear()
        return

      frame = self.__workThread.frame
      job = frame.job
      project = job.project
      self.__widgets['project'].setText(project.name)
      self.__widgets['job'].setText(job.name)
      self.__widgets['frame'].setText(str(frame.time))

      if not self.__workThread.isRunning():
        self.storeLog(self.__workThread.frame)
        self.__workThread = None
        self.__widgets['status'].setText('idle')
        self.setLineEditColor('status', 'yellow')
        return

      currentCondition = 'frame_machineid = %d AND frame_status = \'PROCESSING\'' % self.__machine.id
      frame = zookeeper.zkDB.zkFrame.getByCondition(self.__conn, currentCondition)
      if frame:
        if not frame.id == self.__workThread.frame.id:
          job = frame.job
          self.storeLog(self.__workThread.frame)
          self.__workThread.setFrame(frame)
      return

    else:
      self.__widgets['project'].setText("")
      self.__widgets['job'].setText("")
      self.__widgets['frame'].setText("")

    # only look for work if we have some priority
    if priority == 'OFF':
      self.__widgets['status'].setText('off')
      self.setLineEditColor('status', 'red')
      self.__widgets['project'].setText('')
      self.__widgets['job'].setText('')
      self.__widgets['frame'].setText('')
      self.__widgets['progress'].setValue(0)
      return

    work = self.__conn.call('look_for_work', [self.__machine.id, 1])
    if len(work) == 0:
      self.__widgets['status'].setText('idle')
      self.setLineEditColor('status', 'yellow')
      return

    self.__widgets['progress'].setValue(0)

    # take the frame
    frame = zookeeper.zkDB.zkFrame.getById(self.__conn, id = work[0][0])
    job = frame.job

    # create the right thread
    self.__workThread = zookeeper.zkClient.zkWorkThread.create(self.__conn, frame, self)
    if self.__workThread:
      self.__widgets['status'].setText(priority.lower())
      self.setLineEditColor('status', 'lightgreen')
      self.__workThread.logged.connect(self.onLogged)
      self.__workThread.start()

  def delivery(self):

    output_ids = self.__conn.call('look_for_outputs_to_deliver', [self.__machine.id])
    if len(output_ids) == 0:
      return

    uncmap_machineid = None
    uncmap = None

    frame_ids = {}

    for output_id in output_ids:
      output = zookeeper.zkDB.zkOutput.getById(self.__conn, output_id[0])
      job = output.job
      if job.machine != uncmap_machineid:
        uncmap_machineid = job.machine
        uncmap = zookeeper.zkDB.zkUncMap.getUncMapForMachine(self.__conn, uncmap_machineid)
      scratchPath = output.getScratchFile(self.__cfg)
      networkPath = output.path
      for drive in uncmap:
        if networkPath.lower().startswith(drive.lower()):
          networkPath = uncmap[drive] + networkPath[len(drive):]

      if not os.path.exists(scratchPath):
        continue

      # check if we should overwrite or not
      job = output.job
      if job.overwriteoutputs == 0:
        if os.path.exists(networkPath):
          # redirect the output
          parts = os.path.split(networkPath)
          networkPath = os.path.join(parts[0], job.getScratchKey(), parts[1])
          output.path = networkPath

      networkFolder = os.path.split(networkPath)[0]

      try:
        if not os.path.exists(networkFolder):
          os.makedirs(networkFolder)

        self.log('Delivering frame '+scratchPath+' to '+networkPath)
        shutil.copyfile(scratchPath, networkPath)
        os.remove(scratchPath)
        frame_ids[str(output.frameid)] = True
        output.status = 'DELIVERED'
        output.write()
      except IOError as e:
        self.log('Cannot deliver frame: %s' % e.strerror)
      # except:
      #   pass

    if len(frame_ids.keys()) > 0:
      self.__conn.execute('UPDATE frame SET frame_status = \'DELIVERED\' WHERE frame_id in (%s);' % ','.join(frame_ids.keys()))

  def garbagecollect(self):
    if not self.__cfg.get('scratchdisc_enabled', False):
      return

    log_root = None
    log_root_setting = zookeeper.zkDB.zkSetting.getByName(self.__conn, 'log_root')
    if log_root_setting:
      log_root = log_root_setting.value

    job_ids = self.__conn.call('get_jobs_to_cleanup', [])
    for job_id in job_ids:
      job = zookeeper.zkDB.zkJob(self.__conn, id = job_id[0])
      scratchFolder = job.getScratchFolder(self.__cfg)
      if os.path.exists(scratchFolder):
        self.log('Garbage collecting job folder %s' % scratchFolder)
        shutil.rmtree(scratchFolder, ignore_errors=True)
      if log_root:
        logFolder = os.path.join(log_root, str(job.projectid), str(job.id))
        if os.path.exists(logFolder):
          self.log('Garbage collecting job logs %s' % logFolder)
          shutil.rmtree(logFolder, ignore_errors=True)

    project_ids = self.__conn.call('get_projects_to_cleanup', [])
    for project_id in project_ids:
      project = zookeeper.zkDB.zkProject(self.__conn, id = project_id[0])
      scratchFolder = project.getScratchFolder(self.__cfg)
      if os.path.exists(scratchFolder):
        self.log('Garbage collecting project folder %s' % scratchFolder)
        shutil.rmtree(scratchFolder, ignore_errors=True)
      if log_root:
        logFolder = os.path.join(log_root, str(project.id))
        if os.path.exists(logFolder):
          self.log('Garbage collecting project logs %s' % logFolder)
          shutil.rmtree(logFolder, ignore_errors=True)
