import time
import mysql.connector

class zkConnection(object):

  __ip = None
  __port = None
  __user = None
  __password = None
  __database = None
  __connector = None
  __connected = None
  __lastId = None
  __debug = None
  __lastQuery = None

  def __init__(self, ip = '192.168.1.10', port = 3306, user = 'mysql', password = 'mysql', database = 'zookeeper', debug = False):
    self.__ip = str(ip)
    self.__port = port
    self.__user = user
    self.__password = password
    self.__database = str(database)
    self.__debug = debug
    self.__connected = False
    self.__lastQuery = None
    self.__connector = None

    self.ensureConnection()

  def __del__(self):
    if self.__connector:
      self.__connector.close()
    print 'Connection closed to %s.' % self.__ip

  def clone(self):
    return zkConnection(ip=self.__ip, port=self.__port, user=self.__user, password=self.__password,database=self.__database, debug=self.__debug)

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

  def ensureConnection(self):
    requiresNewConn = False
    if self.__connector is None:
      requiresNewConn = True
    elif not self.__connector.is_connected():
      requiresNewConn = True

    try:
      cursor = self.__connector.cursor()
    except:
      requiresNewConn = True

    if not requiresNewConn:
      return

    tries = 5
    while tries > 0:
      try:
        self.__connector = mysql.connector.connect(user=self.__user, password=self.__password, host=self.__ip, port=self.__port, database=self.__database, buffered=True, connection_timeout=3)
        print 'Connection successful to %s.' % self.__ip
        break
      except mysql.connector.Error as err:
        print("Connection problem: {}".format(err))
      print 'Retrying data base connection...'
      time.sleep(3)
      tries = tries - 1

      if tries == 0:
        raise Exception("Cannot connect to zookeeper database.")

    self.__connected = True
    self.execute(('USE %s;' % self.__database), 'Switching database')

  def execute(self, sql, errorPrefix = "Database"):
    self.ensureConnection()
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
    self.ensureConnection()
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
      self.__connector.commit()
      return result
    except mysql.connector.Error as err:
      print 'Error when calling: << %s >>' % procedure
      print(errorPrefix+": {}".format(err))
    return None
