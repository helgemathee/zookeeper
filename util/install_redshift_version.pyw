import os
import glob
import subprocess
from PySide import QtCore, QtGui
import zipfile
import zookeeper

cfg = zookeeper.zkConfig()

def installRedShiftZip(zipFile):
  version = zipFile.rpartition('_')[2].rpartition('.')[0]
  if len(version) == 0 or version.lower()[0] != 'v':
    QtGui.QMessageBox.critical(None, "ZooKeeper Error", "The zip\n\n%s\n\ndoes not follow the naming convention.\nPlease use zip files with this format:\n\n%s" % (zipFile, 'redshift_v1.2.98.zip'))
    return False
  version = version[1:].lower()

  softimage_workgroup_root = cfg.get('softimage_workgroup_root')
  workgroup = os.path.join(softimage_workgroup_root, 'renderer', 'RedShift', version)
  if not os.path.exists(workgroup):
    os.makedirs(workgroup)
  else:
    QtGui.QMessageBox.critical(None, "ZooKeeper Error", "The folder\n\n%s\n\nalready exists. Please remove it first and restart this utility." % workgroup)
    return False

  print 'Unzipping %s ....' % zipFile
  with zipfile.ZipFile(zipFile, "r") as z:
    z.extractall(os.path.join(workgroup))

  extractTool = os.path.join(softimage_workgroup_root, 'util', 'xsiaddonExtractor.exe')

  addonFiles = glob.glob(os.path.join(workgroup, 'Redshift', 'Plugins', 'Softimage', '*.xsiaddon'))
  for addonFile in addonFiles:
    softimageVersion = addonFile.lower().rpartition('softimage')[2].partition('.')[0].upper()
    addonPath = os.path.join(workgroup, 'Softimage'+softimageVersion)
    cmd = [extractTool, '-o', addonPath, addonFile]
    process = subprocess.Popen(cmd)
    process.wait()

    xmlPath = os.path.join(addonPath, 'Application', 'Plugins', 'bin', 'nt-x86-64', 'pathconfig.xml')
    template = "<path name=\"REDSHIFT_COREDATAPATH\" value=\"%s\" />\n"
    xmlContent = template % "%ZK_SOFTIMAGE_WORKGROUP_ROOT%/renderer/RedShift/%ZK_RENDERER_VERSION%/RedShift"
    open(xmlPath,'w').write(xmlContent)

  print '\nInstalled to '+workgroup

  return True

def main():

  # instantiate the qt app
  app = zookeeper.zkUI.zkApp()

  softimage_workgroup_root = cfg.get('softimage_workgroup_root')
  if not os.path.exists(softimage_workgroup_root):
    QtGui.QMessageBox.critical(None, "ZooKeeper Error", "The path\n\n%s\n\ndoes not exist. Please use the ZooKeeper config to correct this" % softimage_workgroup_root)
    return

  extractTool = os.path.join(softimage_workgroup_root, 'util', 'xsiaddonExtractor.exe')
  if not os.path.exists(extractTool):
    QtGui.QMessageBox.critical(None, "ZooKeeper Error", "The path\n\n%s\n\ndoes not exist. Please use the ZooKeeper config to correct this" % extractTool)
    return

  fields = [{'name': 'RedShift Zip', 'type': 'file', 'value': '', 'filter': '*.zip'}]

  dialog = None
  def onAccepted(fields):
    dialog.close()
    msgBox = QtGui.QMessageBox(None)
    msgBox.setWindowTitle("ZooKeeper")
    msgBox.setText("Performing installation, please stay tuned...")
    msgBox.setStandardButtons(0)
    msgBox.show()
    result = installRedShiftZip(fields[0]['value'])
    msgBox.close()
    if result:
      QtGui.QMessageBox.information(None, "ZooKeeper", "Successfully installed.")

  dialog = zookeeper.zkUI.zkFieldsDialog(fields, onAccepted, None)
  dialog.exec_()

main()
