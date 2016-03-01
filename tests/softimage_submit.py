
projectName = "RND"
inputPath = "X:/exchange/helge/RND/Scenes/city_06.scn"
renderPass = "Default_Pass" # THIS HAS TO BE SPELLED CORRECTLY!!!!!
softimageVersion = "2014"
renderer = "Redshift"
rendererVersion = "1.316"
packageSize = 25
frames = range(1, 101, 1) # start, end+1, step

#------------------------------------

import os
from zookeeper import *

cfg = zkConfig()
conn = zkConnection()

bracket = zkBracket(conn)

project = zkProject.getByName(conn, projectName)
if not project:
  print "Project %s does not exist." % projectName
  exit(1)

inputPath = os.path.normpath(os.path.abspath(inputPath))
if not os.path.exists(inputPath):
  print "Input %s does not exist." % inputPath
  exit(1)

inputFile = zkInput.createNew(conn)
inputFile.path = 'c:/temp/test.png'
bracket.push(inputFile)

job = zkJob.createNew(conn)
job.project = project
job.input = inputFile
job.user = os.environ['USERNAME']
job.name = os.path.split(inputPath)[1].rpartition('.')[0]+'|'+renderPass
job.machine = 1
job.type = 'ALL'
job.dcc = 'Softimage'
job.dccversion = softimageVersion
job.renderer = renderer
job.rendererversion = rendererVersion
bracket.push(job)

for i in frames:
  frame = zkFrame.createNew(conn)
  frame.job = job
  frame.time = i
  frame.priority = 50
  frame.package = i / packageSize
  job.pushFrameForSubmit(frame)

bracket.write()

print 'Job %s submitted with %d frames.' % (job.name, len(frames))
