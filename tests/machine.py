from zookeeper import *

conn = zkConnection()
bracket = zkBracket()

p1 = zkProject.createNew(conn)
p1.name = 'jkn'
bracket.push(p1)

p2 = zkProject.createNew(conn)
p2.name = 'asdad'
bracket.push(p2)

i1 = zkInput.createNew(conn)
i1.path = 'c:/temp/test.png'
bracket.push(i1)

j1 = zkJob.createNew(conn)
j1.project = p2
j1.input = i1
bracket.push(j1)

for i in range(1, 100):
  f = zkFrame.createNew(conn)
  f.job = j1
  f.time = i
  bracket.push(f)

bracket.write()

# machine = zkMachine(conn, asClient = True)
# machine.read()
