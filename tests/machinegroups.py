import zookeeper

conn = zookeeper.zkDB.zkConnection()
conn.setDebug(True)

all = zookeeper.zkDB.zkMachineGroup(conn, id = 1)
test = zookeeper.zkDB.zkMachineGroup(conn, id = 2)

print all.name
print test.name
print len(all.getMachinesInGroup())
print len(test.getMachinesInGroup())
print len(test.getMachinesOutsideGroup())
print test.containsMachine(1)
print test.containsMachine(4)

print test.addMachine(3)
print len(test.getMachinesInGroup())
print test.removeMachine(3)
print len(test.getMachinesInGroup())
