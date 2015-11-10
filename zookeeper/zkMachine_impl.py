import platform
import socket

from zkEntity_impl import zkEntity

def getIps():
  ips = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]
  validIps = []
  for ip in ips:
    if ip.find(':') > -1:
      continue
    validIps += [ip]
  return ','.join(validIps)

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
      self.ip = getIps()
      self.status = 'ONLINE'
      self.lastseen = 'NOW()'
      self.write()
      self.read()

  def __del__(self):
    if self.__asClient:
      self.status = 'OFFLINE'
      self.lastseen = 'NOW()'
      self.write()


