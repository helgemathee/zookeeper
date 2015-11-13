import os
import zookeeper
from PySide import QtCore, QtGui
from zkUtils_impl import zk_validateNetworkFilePath, zk_uncFromDrivePath

class zkSubmitter(object):
  __name = None
  __conn = None
  __app = None
  __machine = None
  __validUncPaths = None

  def __init__(self, name, connection):
    self.__name = name
    self.__conn = connection
    self.__machine = zookeeper.zkDB.zkMachine(self.__conn, asClient = False)
    self.__machine.updateUncMaps()

    self.__validUncPaths = []
    uncPathFieldList = zookeeper.zkDB.zkValidUnc.getFieldList(self.__conn, 'path')
    for uncPath in uncPathFieldList:
      self.__validUncPaths += [uncPath[1]]

  @property
  def name(self):
    return self.__name

  @property
  def connection(self):
    return self.__conn

  # virtual: to be implemented
  def getDCCName(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getDCCVersion(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getRendererName(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getRendererVersion(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getInputPath(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getExternalFilePaths(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getProjectDefaultName(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getJobDefaultName(self):
    raise Exception("To be implemented in specialized class")

  # virtual: to be implemented
  def getExtraFields(self):
    raise Exception("To be implemented in specialized class")

  # virtual: can be overloaded
  def validatePath(self, path, shouldExist = True):
    return zk_validateNetworkFilePath(path, validUncPaths=self.__validUncPaths, shouldExist=shouldExist)

  # virtual: to be implemented
  def createJobFramesAndOutput(self, fields, connection, bracket, project, input):
    raise Exception("To be implemented in specialized class")

  def decorateJobWithDefaults(self, fields, job):
    results = {}
    for field in fields:
      results[field['name']] = field['value']

    user = os.environ.get('USERNAME', None)
    if not user:
      user = os.environ.get('USER', None)
    job.user = user
    job.machine = self.__machine.id
    job.dcc = self.getDCCName()
    job.dccversion = self.getDCCVersion()
    job.renderer = self.getRendererName()
    job.rendererversion = self.getRendererVersion()
    job.priority = results['jobpriority']

    job.mincores = results['mincores']
    job.minramgb = results['minramgb']
    job.mingpuramgb = results['mingpuramgb']

  def createNewProjectWithDialog(self):

    def onAccepted(fields):
      p = zookeeper.zkDB.zkProject.createNew(self.__conn)
      p.name = fields[0]['value']
      p.write()

    dialog = zookeeper.zkUI.zkNewProjectDialog(onAccepted, None)
    dialog.exec_()

  # the main submit process
  def submitWithDialog(self):

    zkSubmitter.__app = zookeeper.zkUI.zkApp()

    # check input and external file paths
    brokenFiles = []
    inputpath = self.getInputPath()
    if not self.validatePath(inputpath, shouldExist=True):
      brokenFiles += [{'path': inputpath, 'group': 'Scenes'}]

    externalfiles = self.getExternalFilePaths()
    for f in externalfiles:
      if not self.validatePath(f['path'], shouldExist=f.get('exist', True)):
        brokenFiles += [f]

    if len(brokenFiles) > 0:
      text = "Some paths are not accessible by other machines on the network.\n"
      text += "Submitting a job is not possible until this is fixed\n."
      print brokenFiles
      for brokenFile in brokenFiles:
        text += '\n%s: %s' % (brokenFile.get('group', 'file'), brokenFile['path'])
      text += "\n\nThis info has been copied to the clipboard."

      clipboard = QtGui.QApplication.clipboard()
      clipboard.setText(text)

      QtGui.QMessageBox.warning(None, 'ZooKeeper Warning', text)
      return

    fields = []
    fields += [{'name': 'dcc', 'value': self.getDCCName(), 'type': 'str', 'readonly': True, 'tooltip': 'The name of the DCC'}]
    fields += [{'name': 'dccversion', 'value': self.getDCCVersion(), 'type': 'str', 'readonly': True, 'tooltip': 'The version of the DCC'}]
    fields += [{'name': 'renderer', 'value': self.getRendererName(), 'type': 'str', 'readonly': True, 'tooltip': 'The name of the renderer'}]
    fields += [{'name': 'rendererversion', 'value': self.getRendererVersion(), 'type': 'str', 'readonly': True, 'tooltip': 'The version of the renderer'}]

    # ensure that we have one project at least!
    pairs = zookeeper.zkDB.zkProject.getNameComboPairs(self.__conn, condition = 'project_type != \'DELETED\'')
    if len(pairs) == 0:
      self.createNewProjectWithDialog()
      pairs = zookeeper.zkDB.zkProject.getNameComboPairs(self.__conn)
      if len(pairs) == 0:
        return

    projectid = pairs[0][0]
    projectname = self.getProjectDefaultName()
    if projectname:
      for pair in pairs:
        if pair[1] == projectname:
          projectid = pair[0]
          break

    fields += [{'name': 'projectid', 'value': projectid, 'type': 'combo', 'comboitems': pairs, 'tooltip': "The name of the project"}]
    fields += [{'name': 'jobname', 'value': self.getJobDefaultName(), 'type': 'str', 'tooltip': "The name of the job", 'readonly': True}]
    fields += [{'name': 'jobpriority', 'value': 50, 'type': 'int', 'tooltip': "The priority of the job"}]
    fields += [{'name': 'mincores', 'value': 4, 'type': 'int', 'tooltip': "The minimum of CPU cores a client machine requires."}]
    fields += [{'name': 'minramgb', 'value': 8, 'type': 'int', 'tooltip': "The minimum of RAM (GB) a client machine requires."}]
    fields += [{'name': 'mingpuramgb', 'value': 2, 'type': 'int', 'tooltip': "The minimum of GPU RAM (GB) a client machine requires."}]
    fields += self.getExtraFields()

    def onAccepted(fields):
      results = {}
      for field in fields:
        results[field['name']] = field['value']

      b = zookeeper.zkDB.zkBracket(self.__conn)
      p = zookeeper.zkDB.zkProject.getById(self.__conn, results['projectid'])

      i = zookeeper.zkDB.zkInput.createNew(self.__conn)
      i.path = zk_uncFromDrivePath(inputpath)
      b.push(i)
      
      self.createJobFramesAndOutput(fields, self.__conn, b, p, i)
      b.write()

      QtGui.QMessageBox.information(None, 'ZooKeeper', 'Job "%s" submitted.' % results['jobname'])

    dialog = zookeeper.zkUI.zkSubmitDialog(fields, onAccepted)
    dialog.exec_()
