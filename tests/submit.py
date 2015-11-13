from zookeeper import *

cfg = zkConfig()
conn = zkConnection()
conn.setDebug(True)

bracket = zkBracket(conn)

p2 = zkProject.createNew(conn)
p2.name = 'TestProject'
bracket.push(p2)

i = zkInput.createNew(conn)
i.path = 'c:/temp/test.png'
bracket.push(i)

j = zkJob.createNew(conn)
j.project = p2
j.input = i
j.user = 'helge'
j.name = 'testrender'
j.machine = 1
j.type = 'ALL'
j.dcc = 'softimage'
j.dccversion = '2014SP2'
j.renderer = 'redshift'
j.rendererversion = '2.0.1'
bracket.push(j)

for i in range(1, 10):
  f = zkFrame.createNew(conn)
  f.job = j
  f.time = i
  j.pushFrameForSubmit(f)

bracket.write()

jobs = p2.getAllJobs()
job = jobs[0]
frames = job.getAllFrames()

for frame in frames:
  outputs = frame.getAllOutputs()
  for output in outputs:
    print output.getScratchFile(cfg)
