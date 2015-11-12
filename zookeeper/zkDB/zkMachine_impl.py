import platform
import socket
import multiprocessing
import psutil
from win_unc.internal.current_state import get_current_net_use_table

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

      self.ramgb = memoryGB
      self.gpuramgb = zkConfig().get('gpuramgb', 1)
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
      self.updatePhysicalState(write = False)
      self._updateHangingFrames(bracket)

      bracket.push(self)
      bracket.write()

  def _updateHangingFrames(self, bracket):
    if not self.id is None:
      cond = 'frame_machineid = %d and (frame_status = \'PROCESSING\' or frame_status = \'COMPLETED\')' % self.id
      frames = zookeeper.zkDB.zkFrame.getAll(self.connection, condition = cond)
      for frame in frames:
        frame.status = 'WAITING'
        bracket.push(frame)

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

    table = get_current_net_use_table()
    for row in table.rows:
      drive = row['local'].get_drive().lower()
      uncpath = row['remote'].get_path().lower()
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
