import zookeeper

class TestSubmitter(zookeeper.zkClient.zkSubmitter):

  def __init__(self, connection):
    super(TestSubmitter, self).__init__('Test', connection)

  def getDCCName(self):
    return 'Test'

  def getDCCVersion(self):
    return '1.0'

  def getRendererName(self):
    return 'Renderer'

  def getRendererVersion(self):
    return '1.0.0'

  def getInputPath(self):
    return 'Z:\\exchange\\test.json'

  def getExternalFilePaths(self):
    return []

  def getProjectDefaultName(self):
    return None

  def getJobDefaultName(self):
    return 'A real good job'

  def getExtraFields(self):
    return [
      {'name': 'maxcount', 'value': 1, 'type': 'int'}
    ]

  def getFramesAndOutput(self, fields, connection, bracket, project, input):
    results = {}
    for field in fields:
      results[field['name']] = field['value']

    # create one job
    job = zookeeper.zkDB.zkJob.createNew(self.connection)
    job.project = project
    job.name = results['jobname']
    job.input = input
    job.type = 'ALL'
    self.decorateJobWithDefaults(fields, job)

    bracket.push(job)

cfg = zookeeper.zkConfig()
conn = zookeeper.zkDB.zkConnection()

submitter = TestSubmitter(conn)

submitter.submitWithDialog()
