import platform
import socket
import multiprocessing
import psutil

import zookeeper
import zookeeper.zkDB
from zookeeper.zkConfig_impl import zkConfig
from zkEntity_impl import zkEntity

def getIps():
  ips = psutil.net_if_addrs()
  ips4v = []
  mac = []
  for ip in ips:
    for nic in ips[ip]:
      if nic.family == 2:
        ips4v += [nic.address]
      elif nic.family == 23:
        mac += [nic.address]
  return (','.join(ips4v), ','.join(mac))

class zkMachine(zkEntity):

  __asClient = None

  def __init__(self, connection, asClient = False, id = None):

    super(zkMachine, self).__init__(connection, table = 'machine', id = id)

    self.__asClient = asClient

    if self.id is None:
      self.read(condition = '%s_name = "%s";' % (self.table, platform.node()), throw = False)

    # we are still not valid, make sure to insert ourselves in the DB
    if self.__asClient or self.id is None:

      bracket = zookeeper.zkDB.zkBracket(self.connection)

      if self.id is None:
        self.name = platform.node()
        self.level = 3
      (ips, mac) = getIps()
      self.ips = ips
      self.macadresses = mac
      self.cores = psutil.cpu_count()

      memory = psutil.virtual_memory()
      memoryGB = int(float(memory.total) / float(1024 * 1024 * 1024) + 0.5)

      cfg = zkConfig()

      self.ramgb = memoryGB
      self.gpuramgb = cfg.get('gpuramgb', 1)

      softimage_versions = cfg.get('softimage_versions', '').split(',')
      dccVersions = []
      for softimage_version in softimage_versions:
        v = softimage_version.strip()
        if len(v) == 0:
          continue
        dccVersions += ['Softimage '+v]
      self.installeddccs = ','.join(dccVersions)

      if self.__asClient:
        self.status = 'ONLINE'
      self.updatePhysicalState(write = False)
      self._updateHangingFrames(bracket)

      bracket.push(self)
      bracket.write()

      self.read()

  def __del__(self):
    if self.__asClient:
      bracket = zookeeper.zkDB.zkBracket(self.connection)

      self.status = 'OFFLINE'
      self.cpuusage = 0
      self.ramavailablemb = 0
      self.ramusedmb = 0
      self.lastseen = 'NOW()'

      self._updateHangingFrames(bracket)

      bracket.push(self)
      bracket.write()

  def _updateHangingFrames(self, bracket):
    if not self.id is None:
      self.connection.call('cleanup_frame_on_machine_start', [self.id])

  def updatePhysicalState(self, write = True):
    self.lastseen = 'NOW()'
    self.cpuusage = int(psutil.cpu_percent()+0.5)
    memory = psutil.virtual_memory()
    self.ramavailablemb = int(float(memory.available) / float(1024 * 1024) + 0.5)
    self.ramusedmb = int(float(memory.used) / float(1024 * 1024) + 0.5)
    if write:
      self.write(throw = False)

  def updateUncMaps(self, write = True):

    bracket = zookeeper.zkDB.zkBracket(self.connection)

    mappedDrives = zookeeper.zkClient.zk_getUncMap()
    for drive in mappedDrives:
      uncpath = mappedDrives[drive]
      uncMap = zookeeper.zkDB.zkUncMap(self.connection, machineid = self.id, drive = drive)
      uncMap.machineid = self.id
      uncMap.drive = drive
      uncMap.uncpath = uncpath
      bracket.push(uncMap)

    bracket.write()

  def sendNotification(self, text, frame = None, severity = 'ERROR'):
    notif = zookeeper.zkDB.zkNotification.createNew(self.connection)
    notif.machine = self
    notif.frame = frame
    notif.severity = severity
    notif.text = text
    notif.write()
