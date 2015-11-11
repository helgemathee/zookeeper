from zkEntity_impl import zkEntity

class zkValidUnc(zkEntity):

  def __init__(self, connection, id = None, drive = None, machineid = None):
    super(zkValidUnc, self).__init__(connection, table = 'validunc', id = id)
