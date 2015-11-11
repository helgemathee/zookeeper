import mysql.connector

class zkConnection(object):

  __connector = None
  __lastId = None
  __debug = None

  def __init__(self, ip = '192.168.1.18', port = 3306, user = 'mysql', password = 'mysql', database = 'zookeeper'):
    try:
      self.__connector = mysql.connector.connect(user=user, password=password, host=ip, port=port, database=database)
      print 'Connection successful.'
    except mysql.connector.Error as err:
      print("Connection problem: {}".format(err))
    self.execute(('USE %s;' % database), 'Switching database')
    self.__debug = False

  def __del__(self):
    self.__connector.close()
    print 'Connection closed.'

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
      cursor.execute(sql, multi = sql.count(';') > 1)
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
