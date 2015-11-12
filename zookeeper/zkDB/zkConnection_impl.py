import mysql.connector

class zkConnection(object):

  __ip = None
  __port = None
  __database = None
  __connector = None
  __connected = None
  __lastId = None
  __debug = None
  __lastQuery = None

  def __init__(self, ip = '192.168.1.10', port = 3306, user = 'mysql', password = 'mysql', database = 'zookeeper', debug = False):
    self.__ip = str(ip)
    self.__port = port
    self.__database = str(database)
    self.__debug = debug
    self.__connected = False
    self.__lastQuery = None

    try:
      self.__connector = mysql.connector.connect(user=user, password=password, host=ip, port=port, database=database, buffered=True)
      print 'Connection successful to %s.' % self.__ip
    except mysql.connector.Error as err:
      print("Connection problem: {}".format(err))
      return
    self.__connected = True
    self.execute(('USE %s;' % database), 'Switching database')

  def __del__(self):
    self.__connector.close()
    print 'Connection closed to %s.' % self.__ip

  @property
  def connected(self):
    return self.__connected

  @property
  def ip(self):
    return self.__ip

  @property
  def port(self):
    return self.__port

  @property
  def database(self):
    return self.__database

  @property
  def lastId(self):
    return self.__lastId

  def setDebug(self, state):
    self.__debug = state

  def execute(self, sql, errorPrefix = "Database"):
    if not self.__connected:
      raise Exception("connection used while not connected.")
    try:
      cursor = self.__connector.cursor()
      if self.__debug:
        print sql
      result = []
      multi = sql.count(';') > 1 or sql.startswith('CALL')
      cursor.execute(sql, multi=multi)
      for r in cursor:
        result += [r]
      iterator = cursor.stored_results()
      for i in iterator:
        result += i.fetchall()
      if sql.startswith('INSERT'):
        self.__lastId = cursor.lastrowid
      if sql.find('INSERT') > -1 or sql.find('UPDATE') > -1 or sql.find('DELETE') > -1 or sql == self.__lastQuery:
        self.__connector.commit()
      self.__lastQuery = sql
      return result
    except mysql.connector.Error as err:
      print 'Error when executing: << %s >>' % sql
      print(errorPrefix+": {}".format(err))
    return None

  def call(self, procedure, args, errorPrefix = "Database"):
    if not self.__connected:
      raise Exception("connection used while not connected.")
    try:
      cursor = self.__connector.cursor()
      if self.__debug:
        strArgs = []
        for arg in args:
          strArgs += [str(arg)]
        print '%s(%s);' % (procedure, ','.join(strArgs))
      cursor.callproc(procedure, args)
      iterator = cursor.stored_results()
      result = []
      for i in iterator:
        result += i.fetchall()
      return result
    except mysql.connector.Error as err:
      print 'Error when calling: << %s >>' % procedure
      print(errorPrefix+": {}".format(err))
    return None
