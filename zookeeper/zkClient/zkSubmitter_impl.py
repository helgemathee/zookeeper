import os
import zookeeper
from PySide import QtCore, QtGui
from zkUtils_impl import zk_validateNetworkFilePath

class zkSubmitter(object):
  __name = None
  __conn = None

  def __init__(self, name, connection):
    self.__name = name
    self.__conn = connection

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

  # virtual: to be implemented
  def getFramesAndOutput(self, fields, connection, bracket, project, input):
    raise Exception("To be implemented in specialized class")

  def decorateJobWithDefaults(self, fields, job):
    results = {}
    for field in fields:
      results[field['name']] = field['value']

    user = os.environ.get('USERNAME', None)
    if not user:
      user = os.environ.get('USER', None)
    job.user = user
    job.dcc = self.getDCCName()
    job.dccversion = self.getDCCVersion()
    job.renderer = self.getRendererName()
    job.rendererversion = self.getRendererVersion()

  def createNewProjectWithDialog(self):

    def onAccepted(fields):
      p = zookeeper.zkDB.zkProject.createNew(self.__conn)
      p.name = fields[0]['value']
      p.write()

    dialog = zookeeper.zkUI.zkNewProjectDialog(onAccepted, None)
    dialog.exec_()

  # the main submit process
  def submitWithDialog(self):

    app = zookeeper.zkUI.zkApp()

    # check input and external file paths
    inputpath = self.getInputPath()
    if not zk_validateNetworkFilePath(inputpath):
      QtGui.QMessageBox.warning(None, 'ZooKeeper Warning', 'The input path\n%s\n is not accessible by other machines on the network.' % inputpath)
      return

    externalfiles = self.getExternalFilePaths()
    for f in externalfiles:
      if not zk_validateNetworkFilePath(f):
        QtGui.QMessageBox.warning(None, 'ZooKeeper Warning', 'The input path\n%s\n is not accessible by other machines on the network.' % f)
        return

    fields = []
    fields += [{'name': 'dcc', 'value': self.getDCCName(), 'type': 'str', 'readonly': True}]
    fields += [{'name': 'dccversion', 'value': self.getDCCVersion(), 'type': 'str', 'readonly': True}]
    fields += [{'name': 'renderer', 'value': self.getRendererName(), 'type': 'str', 'readonly': True}]
    fields += [{'name': 'rendererversion', 'value': self.getRendererVersion(), 'type': 'str', 'readonly': True}]

    # ensure that we have one project at least!
    pairs = zookeeper.zkDB.zkProject.getNameComboPairs(self.__conn)
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
          projectid = pairs[0]
          break

    fields += [{'name': 'projectid', 'value': projectid, 'type': 'combo', 'comboitems': pairs}]
    fields += [{'name': 'jobname', 'value': self.getJobDefaultName(), 'type': 'str'}]
    fields += self.getExtraFields()

    def onAccepted(fields):
      results = {}
      for field in fields:
        results[field['name']] = field['value']

      b = zookeeper.zkDB.zkBracket(self.__conn)
      p = zookeeper.zkDB.zkProject.getById(self.__conn, results['projectid'])

      i = zookeeper.zkDB.zkInput.createNew(self.__conn)
      i.path = inputpath
      b.push(i)
      
      self.getFramesAndOutput(fields, self.__conn, b, p, i)
      b.write()

      QtGui.QMessageBox.information(None, 'ZooKeeper', 'Job "%s" submitted.' % results['jobname'])

    dialog = zookeeper.zkUI.zkSubmitDialog(fields, onAccepted)
    dialog.exec_()
