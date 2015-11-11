from zookeeper import *

cfg = zkConfig()
conn = zkConnection()
# conn.setDebug(True)

p2 = zkProject.createNew(conn)
# p2.name = 'TestProject'
p2.write()

j1 = zkJob.createNew(conn)
j1.project = p2
j1.write()
