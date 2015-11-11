import platform
import socket
import multiprocessing
import psutil

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

    if self.__asClient:
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
      self.updatePhysicalState()
      self.read()

  def __del__(self):
    if self.__asClient:
      self.status = 'OFFLINE'
      self.updatePhysicalState()

  def updatePhysicalState(self, write = True):
    self.lastseen = 'NOW()'
    self.cpuusage = int(psutil.cpu_percent()+0.5)
    memory = psutil.virtual_memory()
    self.ramavailablemb = int(float(memory.available) / float(1024 * 1024) + 0.5)
    self.ramusedmb = int(float(memory.used) / float(1024 * 1024) + 0.5)
    if write:
      self.write()

  def sendNotification(self, text, frame = None, severity = 'ERROR'):
    notif = zookeeper.zkDB.zkNotification.createNew(self.connection)
    notif.machine = self
    notif.frame = frame
    notif.severity = severity
    notif.text = text
    notif.write()
