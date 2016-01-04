import datetime

class zkEntity(object):

  __table = None
  __conn = None
  __id = None
  __initiallyRead = None
  __fields = None
  __fieldsChanged = None
  __tableFields = {}

  def __init__(self, connection, table, id = None):

    self.__conn = connection
    self.__table = '' + str(table)
    self.__id = id
    self.__fieldsChanged = {}

    self.ensureTableFieldsExists(table, self.__conn)

    self.__fields = {}
    for field in zkEntity.__tableFields[table]:
      self.__fields[field] = None

    self.__initiallyRead = True
    if not self.__id is None:
      self.__initiallyRead = False

  @staticmethod
  def ensureTableFieldsExists(table, conn):
    if not table in zkEntity.__tableFields:
      cols = conn.execute('DESCRIBE %s;' % table)
      fields = []
      for col in cols:
        fields += [str(col[0])]
      zkEntity.__tableFields[table] = fields

  def __getattribute__(self, name):
    try:
      return object.__getattribute__(self, name)
    except AttributeError as e:
      if not self.__initiallyRead:
        self.read()
      key = self.__table + '_' + name
      if key in self.__fields:
        return self.__fields[key]
      raise e

  def __setattr__(self, name, value):
    if not name.startswith('_') and not name in ['id', 'table', 'fields', 'connection']:
      if not self.__initiallyRead and not self.__id is None:
        self.read()
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

  # may be overloaded
  @classmethod
  def getUIFields(cls, conn):
    table = cls.getTableName()
    cls.ensureTableFieldsExists(table, conn)
    return zkEntity.__tableFields[table]

  # may be overloaded
  @classmethod
  def getMainOrderField(cls):
    table = cls.getTableName()
    return table + '_id'

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
        self.__initiallyRead = True
      self.__fieldsChanged = {}
      return

    if throw:
      raise(Exception('zkEntity::read called without an id.'))

  def write(self, throw = True):
    if len(self.__fieldsChanged.keys()) == 0:
      # if throw:
      #   print '%s: Nothing to write. Please set some fields first.' % self.__class__.__name__
      return

    fieldNames = []
    fieldValues = []
    fieldPairs = []

    for fieldName in zkEntity.__tableFields[self.__table]:
      if fieldName in self.__fieldsChanged:
        fieldValue = self.__fields[fieldName]
        if fieldValue is None:
          continue
        if (isinstance(fieldValue, str) or isinstance(fieldValue, unicode)) and fieldValue.find('()') == -1:
          fieldValue = repr(str(fieldValue))
        fieldNames += [fieldName]
        fieldValues += [str(fieldValue)]
        fieldPairs += [fieldName+'='+str(fieldValue)]

    if len(fieldNames) == 0:
      return

    if self.__id is None:
      sql = 'INSERT INTO %s (%s) VALUES(%s);' % (self.table, ','.join(fieldNames), ','.join(fieldValues))
    else:
      sql = 'UPDATE %s SET %s WHERE %s_id = %d;' % (self.table, ','.join(fieldPairs), self.table, self.id)

    self.execute(sql)
    self.__fields[self.table+'_id'] = self.__id
    self.__fieldsChanged = {}

  @classmethod
  def getTableName(cls):
    return cls.__name__[2:].lower()

  def delete(self):
    if self.id is None:
      return
    sql = 'DELETE FROM %s WHERE %s_id = %d;' % (self.table, self.table, self.id)
    self.execute(sql)

    self.__id = None
    self.__initiallyRead = False
    self.__fields = {}
    for field in zkEntity.__tableFields[self.table]:
      self.__fields[field] = None
    self.__fieldsChanged = {}

  @classmethod
  def deleteAll(cls, conn, condition):
    if not condition:
      return
    table = cls.getTableName()
    sql = 'DELETE FROM %s WHERE %s;' % (table, condition)
    conn.execute(sql, errorPrefix = table)

  @classmethod
  def getAll(cls, conn, condition=None, limit=None, order=None, additionalTables=None):
    table = cls.getTableName()
    tables = [table]
    if additionalTables:
      tables += additionalTables
    sql = 'SELECT %s_id FROM %s' % (table, ', '.join(tables))
    if not condition is None:
      sql += ' WHERE %s' % str(condition)
    if not limit is None:
      sql += ' LIMIT %s' % str(limit)
    if not order is None:
      sql += ' ORDER BY %s' % str(order)
    sql += ';'
    ids = conn.execute(sql, errorPrefix=table)
    result = []
    for id in ids:
      result += [cls(conn, id=id[0])]
    return result

  @classmethod
  def getByCondition(cls, conn, condition, additionalTables = None):
    table = cls.getTableName()
    tables = [table]
    if additionalTables:
      tables += additionalTables
    sql = 'SELECT %s_id FROM %s WHERE %s LIMIT 1;' % (table, ','.join(tables), condition)
    ids = conn.execute(sql, errorPrefix=table)
    for id in ids:
      return cls(conn, id=id[0])
    return None

  @classmethod
  def getByName(cls, conn, name):
    table = cls.getTableName()
    condition = '%s_name = \'%s\'' % (table, name)
    return cls.getByCondition(conn, condition)

  @classmethod
  def getById(cls, conn, id):
    return cls(conn, id = id)

  @classmethod
  def createNew(cls, conn):
    return cls(conn)

  @classmethod
  def getFieldList(cls, conn, field, condition=None):
    table = cls.getTableName()
    sql = 'SELECT %s_id, %s_%s FROM %s %s ORDER BY %s_%s ASC;' % (table, table, field, table, 'WHERE '+condition if condition else '', table, field)
    results = conn.execute(sql, errorPrefix=table)
    pairs = []
    for r in results:
      pairs += [[r[0], r[1]]]
    return pairs

  @classmethod
  def getNameComboPairs(cls, conn, condition = None):
    return cls.getFieldList(conn, 'name', condition=condition)

  @classmethod
  def getEnumComboPairs(cls, conn, field):
    table = cls.getTableName()
    sql = 'SHOW COLUMNS FROM %s WHERE Field = \'%s_%s\';' % (table, table, field)
    results = conn.execute(sql, errorPrefix=table)
    if len(results) == 0:
      return []
    enum = str(results[0][1])
    values = enum.partition('(')[2].partition(')')[0].split(',')
    result = []
    for value in values:
      result += [[len(result), value.strip('\'')]]
    return result
