import mysql.connector

class zkConnection(object):

  __ip = None
  __connector = None
  __lastId = None
  __debug = None

  def __init__(self, ip = '192.168.1.18', port = 3306, user = 'mysql', password = 'mysql', database = 'zookeeper'):
    self.__ip = str(ip)
    try:
      self.__connector = mysql.connector.connect(user=user, password=password, host=ip, port=port, database=database)
      print 'Connection successful to %s.' % self.__ip
    except mysql.connector.Error as err:
      print("Connection problem: {}".format(err))
    self.execute(('USE %s;' % database), 'Switching database')
    self.__debug = False

  def __del__(self):
    self.__connector.close()
    print 'Connection closed to %s.' % self.__ip

  @property
  def ip(self):
    return self.__ip

  @property
  def lastId(self):
    return self.__lastId

  def setDebug(self, state):
    self.__debug = state

  def execute(self, sql, errorPrefix = "Database"):
    try:
      cursor = self.__connector.cursor()
      if self.__debug:
        print sql
      cursor.execute(sql, multi = (sql.count(';') > 1 or sql.startswith('CALL')))
      result = []
      for r in cursor:
        result += [r]
      if sql.startswith('INSERT'):
        self.__lastId = cursor.lastrowid
      if sql.find('INSERT') > -1 or sql.find('UPDATE') > -1 or sql.find('DELETE') > -1:
        self.__connector.commit()
      return result
    except mysql.connector.Error as err:
      print 'Error when executing: << %s >>' % sql
      print(errorPrefix+": {}".format(err))
    return None

  def call(self, procedure, args, errorPrefix = "Database"):
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
