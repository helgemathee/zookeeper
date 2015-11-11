import zookeeper

class zkSoftimageSubmitter(zookeeper.zkClient.zkSubmitter):

  def __init__(self, connection):
    super(zkSoftimageSubmitter, self).__init__('Softimage', connection)
