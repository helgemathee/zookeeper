from zkEntity_impl import zkEntity

class zkProject(zkEntity):

  def __init__(self, connection, id = None):
    super(zkProject, self).__init__(connection, table = 'project', id = id)
