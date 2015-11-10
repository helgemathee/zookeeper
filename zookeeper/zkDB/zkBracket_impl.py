
class zkBracket(object):

  __entities = []

  def __init__(self):
    self.__entities = []

  def push(self, sql):
    self.__entities += [sql]

  def write(self):
    for entity in self.__entities:
      entity.write()
    self.__entities = []
