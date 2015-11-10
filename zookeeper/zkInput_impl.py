from zkEntity_impl import zkEntity

class zkInput(zkEntity):

  def __init__(self, connection, id = None):
    super(zkInput, self).__init__(connection, table = 'input', id = id)
