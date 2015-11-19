import os
import zookeeper
from zkEntity_impl import zkEntity
from zkProject_impl import zkProject
from zkJob_impl import zkJob

class zkFrame(zkEntity):

  __tmpProject = None
  __tmpJob = None
  __tmpMachine = None
  __tmpOutputs = None

  def __init__(self, connection, id = None):
    super(zkFrame, self).__init__(connection, table = 'frame', id = id)
    self.__tmpProject = None
    self.__tmpJob = None
    self.__tmpMachine = None
    self.__tmpOutputs = []

  def __getProject(self):
    if self.id is None:
      return self.__tmpProject
    return zkProject(self.connection, self.projectid)

  def __setProject(self, value):
    self.__tmpProject = value

  def __getJob(self):
    if self.id is None:
      return self.__tmpJob
    return zkJob(self.connection, self.jobid)

  def __setJob(self, value):
    self.project = value.project
    self.__tmpJob = value

  def __getMachine(self):
    if self.id is None:
      return self.__tmpMachine
    return zookeeper.zkDB.zkMachine(self.connection, self.machineid)

  def __setMachine(self, value):
    self.__tmpMachine = value

  project = property(__getProject, __setProject)
  job = property(__getJob, __setJob)
  machine = property(__getMachine, __setMachine)

  def pushOutputForSubmit(self, output):
    self.__tmpOutputs += [output]

  @property
  def outputsForSubmit(self):
    return self.__tmpOutputs

  def write(self):

    if not self.__tmpProject is None:
      self.projectid = self.__tmpProject.id
      self.__tmpProject = None
    if not self.__tmpJob is None:
      self.jobid = self.__tmpJob.id
      self.__tmpJob = None
    if not self.__tmpMachine is None:
      self.machineid = self.__tmpMachine.id
      self.__tmpMachine = None

    super(zkFrame, self).write()

    if len(self.__tmpOutputs) > 0:

      outputs = []
      for i in range(len(self.__tmpOutputs)):
        o = self.__tmpOutputs[i]
        outputs += [[
          str(self.projectid),
          str(self.jobid),
          str(self.id),
          repr(str(o.name)),
          repr(str(o.path)),
        ]]

      sql = "INSERT into output (output_projectid, output_jobid, output_frameid, output_name, output_path) VALUES "

      for i in range(len(outputs)):
        if i > 0:
          sql += ','
        sql += '(' + ','.join(outputs[i]) + ')'
      sql += ';'
      self.connection.execute(sql)

      self.__tmpOutputs = []   

  def getAllOutputs(self):
    return zookeeper.zkDB.zkOutput.getAll(self.connection, condition = 'output_frameid=%d' % self.id)

  def getScratchKey(self):
    return 'frame_'+str(self.id)

  def getScratchFolder(self, config):
    return self.job.getScratchFolder(config)

  def getLogFilePath(self):
    setting = zookeeper.zkDB.zkSetting.getByName(self.connection, 'log_root')
    if setting:
      folder = os.path.join(setting.value, str(self.projectid), str(self.jobid))
      if not os.path.exists(folder):
        try:
          os.makedirs(folder)
        except:
          return None
      path = os.path.join(folder, str(self.id)+'.log')
      return path
    return None

  def setAsFailed(self):
    self.connection.call("set_frame_failed", [self.id])

  def setAsProcessing(self, machine_id):
    self.connection.call("set_frame_processing", [self.id, machine_id])
