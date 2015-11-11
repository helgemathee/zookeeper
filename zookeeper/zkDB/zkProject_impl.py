import os
import zookeeper
from zkEntity_impl import zkEntity

class zkProject(zkEntity):

  def __init__(self, connection, id = None):
    super(zkProject, self).__init__(connection, table = 'project', id = id)

  def getAllJobs(self):
    return zookeeper.zkDB.zkJob.getAll(self.connection, condition = 'job_projectid='+str(self.id))

  def getScratchKey(self):
    return self.name+'_'+str(self.id)

  def getScratchFolder(self, config):
    enabled = config.get('scratchdisc_enabled', False)
    if not enabled:
      return None
    return os.path.normpath(os.path.join(config.get('scratchdisc_folder', os.environ['TEMP']), self.getScratchKey()))
