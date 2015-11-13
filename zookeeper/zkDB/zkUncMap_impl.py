from zkEntity_impl import zkEntity

class zkUncMap(zkEntity):

  def __init__(self, connection, id = None, drive = None, machineid = None):
    super(zkUncMap, self).__init__(connection, table = 'uncmap', id = id)

    if drive and machineid:
      self.read(condition = 'uncmap_machineid = %d and uncmap_drive = \'%s\'' % (machineid, drive.lower()), throw = False)

  @classmethod
  def getUncMapForMachine(cls, connection, machineid):
    result = {}
    maps = cls.getAll(connection, condition = 'uncmap_machineid = '+str(machineid))
    for m in maps:
      result[m.drive] = m.uncpath
    return result
