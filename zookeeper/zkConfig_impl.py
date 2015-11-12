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
    self.set('softimage_root_folder', 'C:/Program Files/Autodesk', type = 'folder', tooltip = 'Normally the Autodesk main folder.', onlyIfNotExists = True)
    self.set('softimage_user_root', 'c:\\temp\\zookeeper\\Softimage\\user', type = 'folder', tooltip = 'The softimage render user folder.', onlyIfNotExists = True)
    self.set('softimage_workgroup_root', 'c:\\temp\\zookeeper\\Softimage\\workgroups', type = 'folder', tooltip = 'The softimage workgroup root folder.', onlyIfNotExists = True)
    self.set('gpuramgb', 1, type='int', tooltip = 'The number of GBs of RAM on the largest GPU.', onlyIfNotExists = True)
    self.set('scratchdisc_enabled', False, type='bool', tooltip = 'Checking this enables a local scratch disc.', onlyIfNotExists = True)
    self.set('scratchdisc_folder', 'c:/temp/scratch', type='folder', tooltip = 'The location of the local scratch disc.', onlyIfNotExists = True)
    self.set('scratchdisc_sizegb', 100, type='int', tooltip = 'The size in GB for the local scratch disc.', onlyIfNotExists = True)
    self.set('clientinterval', 5, type='int', tooltip = 'The interval in seconds in which the client checks for work.', onlyIfNotExists = True)

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

  def set(self, name, value, type = 'str', tooltip = None, onlyIfNotExists = False):
    if name == '':
      return

    for i in range(len(self.__fields)):
      field = self.__fields[i]
      if field['name'] == name:
        if onlyIfNotExists:
          return
        field['value'] = value
        if tooltip:
          field['tooltip'] = tooltip
        self._write()
        return
    self.__fields += [{'name': name, 'value': value, 'type': type, 'tooltip': tooltip}]
    self._write()

  def getFields(self):
    return self.__fields
