from zookeeper import *

conn = zkConnection()
conn.setDebug(True)
bracket = zkBracket()

p2 = zkProject.createNew(conn)
p2.name = 'asdad'
p2.dcc = 'softimage'
p2.renderer = 'redshift'
bracket.push(p2)

i1 = zkInput.createNew(conn)
i1.path = 'c:/temp/test.png'
bracket.push(i1)

j1 = zkJob.createNew(conn)
j1.project = p2
j1.input = i1
j1.user = 'helge'
j1.type = 'preview'
bracket.push(j1)

for i in range(1, 10):
  f = zkFrame.createNew(conn)
  f.job = j1
  f.time = i
  bracket.push(f)

  o = zkOutput.createNew(conn)
  o.frame = f
  o.path = "//domain/test/test/%d.png" % i
  bracket.push(o)

bracket.write()

# machine = zkMachine(conn, asClient = True)
# machine.read()
