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
    self.set('gpuramgb', 1, type='int', label = 'Available GPU RAM', tooltip = 'The number of GBs of RAM on the largest GPU.', onlyIfNotExists = True)
    self.set('scratchdisc_enabled', False, type='bool', label = 'Scratch disc enabled', tooltip = 'Checking this enables a local scratch disc.', onlyIfNotExists = True)
    self.set('scratchdisc_folder', 'c:/temp/scratch', type='folder', label = 'Scratch disc location', tooltip = 'The location of the local scratch disc.', onlyIfNotExists = True)
    self.set('scratchdisc_sizegb', 100, type='int', label = 'Scratch disc size (GB)', tooltip = 'The size in GB for the local scratch disc.', onlyIfNotExists = True)
    self.set('softimage_root_folder', 'C:/Program Files/Autodesk', type = 'folder', label = 'Softimage installation location', tooltip = 'Normally the Autodesk main folder.', onlyIfNotExists = True)
    self.set('softimage_user_root', 'c:\\temp\\users', type = 'folder', label = 'Temporary user location', tooltip = 'The temporary softimage render user folder.', onlyIfNotExists = True)
    self.set('softimage_workgroup_root', 'c:\\temp\\workgroups', type = 'folder', label = 'Temporary workgroup location', tooltip = 'The root folder for the softimage workgroup.', onlyIfNotExists = True)
    self.set('softimage_flipbook_version', '2014 SP2', type = 'str', label = 'Softimage Flipbook Version', tooltip = 'The softimage version to use for flipbook.', onlyIfNotExists = True)
    self.set('softimage_versions', '2014', type = 'str', label = 'Softimage Versions', tooltip = 'The softimage versions installed on this machine (without SP), comma separated.', onlyIfNotExists = True)

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

  def set(self, name, value, type = 'str', tooltip = None, onlyIfNotExists = False, label = None):
    if name == '':
      return

    for i in range(len(self.__fields)):
      field = self.__fields[i]
      if field['name'] == name:
        if tooltip:
          field['tooltip'] = tooltip
        if label:
          field['label'] = label
        if onlyIfNotExists:
          return
        field['value'] = value
        self._write()
        return
    field = {'name': name, 'value': value, 'type': type, 'tooltip': tooltip}
    if label:
      field['label'] = label
    self.__fields += [field]
    self._write()

  def getFields(self):
    return self.__fields
