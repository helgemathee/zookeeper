from zkEntity_impl import zkEntity

class zkSetting(zkEntity):

  def __init__(self, connection, id = None, drive = None, machineid = None):
    super(zkSetting, self).__init__(connection, table = 'setting', id = id)
