from zookeeper import *

conn = zkConnection()
bracket = zkCommit()

p1 = zkProject.createNew(conn)
p1.name = 'jkn'

p2 = zkProject.createNew(conn)
p2.name = 'asdad'

i1 = zkInput.createNew(conn)
i1.path = 'c:/temp/test.png'

j1 = zkJob.createNew(conn)
j1.project = p2
j1.input = i1

bracket.push(p1)
bracket.push(p2)
bracket.push(i1)
bracket.push(j1)

bracket.execute()

# machine = zkMachine(conn, asClient = True)
# machine.read()
