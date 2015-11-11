import datetime

class zkEntity(object):

  __table = None
  __conn = None
  __id = None
  __fields = None
  __fieldsChanged = None
  __tableFields = {}

  def __init__(self, connection, table, id = None):

    self.__conn = connection
    self.__table = '' + str(table)
    self.__id = id
    self.__fieldsChanged = {}

    if not table in zkEntity.__tableFields:
      cols = self.__conn.execute('DESCRIBE %s;' % table)
      fields = []
      for col in cols:
        fields += [str(col[0])]
      zkEntity.__tableFields[table] = fields

    self.__fields = {}
    for field in zkEntity.__tableFields[table]:
      self.__fields[field] = None

    if not self.__id is None:
      self.read()

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, name)
    except AttributeError as e:
      key = self.__table + '_' + name
      if key in self.__fields:
        return self.__fields[key]
      raise e

  def __setattr__(self, name, value):
    if not name in ['id', 'table', 'fields', 'connection']:
      if not self.__table is None and not self.__fields is None:
        key = self.__table + '_' + name
        if key in self.__fields:
          if not self.__fields[key] == value:
            self.__fields[key] = value
            self.__fieldsChanged[key] = True
          return
    object.__setattr__(self, name, value)

  @property
  def id(self):
    return self.__id

  @property
  def table(self):
    return self.__table

  @property
  def fields(self):
    result = []
    for field in zkEntity.__tableFields[self.__table]:
      result += [field[len(self.table)+1:]]
    return result

  @property
  def connection(self):
    return self.__conn

  @property
  def values(self):
    result = []
    for field in zkEntity.__tableFields[self.__table]:
      result += [self.__fields[field]]
    return result

  def execute(self, sql):
    result = self.__conn.execute(sql, errorPrefix = self.table)
    if sql.startswith('INSERT'):
      self.__id = self.__conn.lastId
    return result

  def read(self, id = None, condition = None, throw = True):
    if not id is None:
      self.__id = id
    if not self.__id is None:
      condition = '%s_id = %d' % (self.__table, self.__id)

    if not condition is None:
      fieldNames = ','.join(zkEntity.__tableFields[self.__table])
      sql = "SELECT %s from %s WHERE %s" % (fieldNames, self.__table, condition)
      fields = self.execute(sql)
      if len(fields) > 0:
        if len(fields[0]) == len(zkEntity.__tableFields[self.__table]):
          for i in range(len(zkEntity.__tableFields[self.__table])):
            field = zkEntity.__tableFields[self.__table][i]
            value = fields[0][i]
            if isinstance(value, datetime.datetime):
              value = value.strftime("%Y-%m-%d %H::%M::%S")
            self.__fields[field] = value
          self.__id = self.__fields[self.__table+'_id']
      self.__fieldsChanged = {}
      return

    if throw:
      raise(Exception('zkEntity::read called without an id.'))

  def write(self):
    if len(self.__fieldsChanged.keys()) == 0:
      return

    fieldNames = []
    fieldValues = []
    fieldPairs = []
    for fieldName in zkEntity.__tableFields[self.__table]:
      if fieldName in self.__fieldsChanged:
        fieldValue = self.__fields[fieldName]
        if fieldValue is None:
          continue
        if isinstance(fieldValue, str) and not fieldValue.endswith('()'):
          fieldValue = '"%s"' % fieldValue
        fieldNames += [fieldName]
        fieldValues += [str(fieldValue)]
        fieldPairs += [fieldName+'='+str(fieldValue)]

    if len(fieldNames) == 0:
      return

    if self.__id is None:
      sql = 'INSERT INTO %s (%s) VALUES(%s) ON DUPLICATE KEY UPDATE %s' % (self.table, ','.join(fieldNames), ','.join(fieldValues), ','.join(fieldPairs))
    else:
      sql = 'UPDATE %s SET %s WHERE %s_id = %d;' % (self.table, ','.join(fieldPairs), self.table, self.id)

    self.execute(sql)
    self.__fields[self.table+'_id'] = self.__id
    self.__fieldsChanged = {}

  @classmethod
  def getTableName(cls):
    return cls.__name__[2:].lower()

  @classmethod
  def getAll(cls, conn, condition=None, limit=None, order=None):
    table = cls.getTableName()
    sql = 'SELECT %s_id FROM %s' % (table, table)
    if not condition is None:
      sql += 'WHERE %s' % str(condition)
    if not limit is None:
      sql += 'LIMIT %s' % str(limit)
    if not order is None:
      sql += 'ORDER BY %s' % str(order)
    sql += ';'
    ids = conn.execute(sql, errorPrefix=table)
    result = []
    for id in ids:
      result += [cls(conn, id=id[0])]
    return result

  @classmethod
  def getByName(cls, conn, name):
    table = cls.getTableName()
    sql = 'SELECT %s_id FROM %s WHERE %s_name = "%s";' % (table, table, table, name)
    ids = conn.execute(sql, errorPrefix=table)
    for id in ids:
      return cls(conn, id=id[0])
    return None

  @classmethod
  def createNew(cls, conn):
    return cls(conn)


