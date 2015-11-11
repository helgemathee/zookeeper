from zookeeper import *

cfg = zkConfig()
conn = zkConnection()
# conn.setDebug(True)

bracket = zkBracket(conn)

p2 = zkProject.createNew(conn)
p2.name = 'TestProject'
bracket.push(p2)

i1 = zkInput.createNew(conn)
i1.path = 'c:/temp/test.png'
bracket.push(i1)

j1 = zkJob.createNew(conn)
j1.project = p2
j1.input = i1
j1.user = 'helge'
j1.name = 'testrender'
j1.type = 'ALL'
j1.dcc = 'softimage'
j1.dccversion = '2014SP2'
j1.renderer = 'redshift'
j1.rendererversion = '2.0.1'
bracket.push(j1)

for i in range(1, 10):
  f = zkFrame.createNew(conn)
  f.job = j1
  f.time = i
  bracket.push(f)

  o = zkOutput.createNew(conn)
  o.frame = f
  o.name = 'diffuse'
  o.path = "//domain/test/test/%d.png" % i
  bracket.push(o)

bracket.write()

jobs = p2.getAllJobs()
job = jobs[0]
frames = job.getAllFrames()

for frame in frames:
  outputs = frame.getAllOutputs()
  for output in outputs:
    print output.getScratchFile(cfg)
