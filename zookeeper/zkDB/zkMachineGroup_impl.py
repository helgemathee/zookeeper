import platform
import socket
import multiprocessing
import psutil

import zookeeper
import zookeeper.zkDB
from zookeeper.zkConfig_impl import zkConfig
from zkEntity_impl import zkEntity

class zkMachineGroup(zkEntity):

  def __init__(self, connection, id = None):
    super(zkMachineGroup, self).__init__(connection, table = 'machinegroup', id = id)

  def delete(self):
    if self.id == 1:
      return False
    return super(zkMachineGroup, self).delete(procedure = 'delete_group')

  def containsMachine(self, machine_id):
    if self.id == 1:
      return True
    results = self.execute('SELECT * FROM membership WHERE membership_machine = %d AND membership_machinegroup = %d' % (machine_id, self.id))
    return len(results) > 0

  def getMachinesInGroup(self):
    cond = 'machine_id = membership_machine AND membership_machinegroup = %d' % self.id
    if self.id == 1: # all group
      return zookeeper.zkDB.zkMachine.getAll(self.connection, condition = 'machine_id > 0')
    return zookeeper.zkDB.zkMachine.getAll(self.connection, condition = cond, additionalTables = ['membership'], order = 'machine_name ASC')

  def getMachinesOutsideGroup(self):
    if self.id == 1:
      return []
    sql = 'SELECT machine_id FROM machine WHERE machine_id NOT IN ('
    sql += 'SELECT machine_id FROM machine, membership WHERE machine_id = membership_machine AND membership_machinegroup = %d)' % self.id
    results = self.execute(sql)
    machines = []
    for result in results:
      machines += [zookeeper.zkDB.zkMachine(connection = self.connection, id = result[0])]
    return machines

  def addMachine(self, machine_id):
    if self.id == 1:
      return True
    if self.containsMachine(machine_id):
      return False
    memberShip = zookeeper.zkDB.zkMemberShip(connection = self.connection)
    memberShip.machine = machine_id
    memberShip.machinegroup = self.id
    memberShip.write()
    return True

  def removeMachine(self, machine_id):
    if self.id == 1:
      return False
    if not self.containsMachine(machine_id):
      return False
    zookeeper.zkDB.zkMemberShip.deleteAll(conn = self.connection, condition = 'membership_machine = %d AND membership_machinegroup = %d' % (machine_id, self.id))
    return True

