
class zkBracket(object):

  __entities = []
  __conn = None

  def __init__(self, conn):
    self.__entities = []
    self.__conn = conn

  def push(self, sql):
    self.__entities += [sql]

  def write(self):
    if len(self.__entities) == 0:
      return;

    tables = {}
    for entity in self.__entities:
      tables[entity.table] = True

    sql = []
    for table in tables:
      sql += ['LOCK TABLES %s WRITE;' % table]
    self.__conn.execute('\n'.join(sql))
    for entity in self.__entities:
      entity.write()
    self.__entities = []
    self.__conn.execute('UNLOCK TABLES;')
