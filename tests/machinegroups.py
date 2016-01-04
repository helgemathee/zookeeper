import zookeeper

conn = zookeeper.zkDB.zkConnection()
# conn.setDebug(True)

all = zookeeper.zkDB.zkMachineGroup(conn, id = 1)
test = zookeeper.zkDB.zkMachineGroup(conn)
test.name = 'test'
test.write()

print all.name
print test.name
print len(all.getMachinesInGroup())
print len(test.getMachinesInGroup())
print len(test.getMachinesOutsideGroup())

test.addMachine(3)
print len(test.getMachinesInGroup())
print test.containsMachine(3)
test.removeMachine(3)
print len(test.getMachinesInGroup())
print test.containsMachine(3)
print len(test.getMachinesOutsideGroup())

test.delete()
