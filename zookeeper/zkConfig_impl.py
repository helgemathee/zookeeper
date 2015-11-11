import os
import sys
import json

class zkConfig(object):

  __path = None
  __fields = None

  def __init__(self):

    self.__path = str(__file__)
    self.__path = os.path.join(os.path.split(self.__path)[0], 'config.json')
    self.__fields = []
    self._read()
    
    # here you should define all fields
    # types supported are 'folder', 'str', 'int', 'bool'
    self.set('softimage_root_folder', 'C:/Program Files/Autodesk', type = 'folder', onlyIfNotExists = True)
    self.set('gpuramgb', 1, type='int', onlyIfNotExists = True)
    self.set('scratchdisc_enabled', False, type='bool', onlyIfNotExists = True)
    self.set('scratchdisc_folder', 'c:/temp/scratch', type='folder', onlyIfNotExists = True)
    self.set('scratchdisc_sizegb', 100, type='int', onlyIfNotExists = True)

  def _read(self):
    if os.path.exists(self.__path):
      self.__fields = json.loads(open(self.__path, 'rb').read())
      return True
    return False

  def _write(self):
    open(self.__path, 'w').write(json.dumps(self.__fields, indent = 2))

  def get(self, name, defaultValue = ''):
    if name == '':
      return defaultValue

    if os.path.exists(self.__path):
      self.__fields = json.loads(open(self.__path, 'rb').read())

    for i in range(len(self.__fields)):
      field = self.__fields[i]
      if field['name'] == name:
        return field['value']
    return defaultValue

  def set(self, name, value, type = 'str', onlyIfNotExists = False):
    if name == '':
      return

    for i in range(len(self.__fields)):
      field = self.__fields[i]
      if field['name'] == name:
        if onlyIfNotExists:
          return
        field['value'] = value
        self._write()
        return
    self.__fields += [{'name': name, 'value': value, 'type': type}]
    self._write()

  def getFields(self):
    return self.__fields
