import os
import glob
import subprocess
from PySide import QtCore, QtGui
import zipfile
import zookeeper

cfg = zookeeper.zkConfig()

def installRedShiftZip(softimage_workgroup_root, zipFile):
  version = zipFile.rpartition('_')[2].rpartition('.')[0]
  if len(version) == 0 or version.lower()[0] != 'v':
    QtGui.QMessageBox.critical(None, "ZooKeeper Error", "The zip\n\n%s\n\ndoes not follow the naming convention.\nPlease use zip files with this format:\n\n%s" % (zipFile, 'redshift_v1.2.98.zip'))
    return False
  version = version[1:].lower()
  parts = version.partition('.')
  version = parts[0] + '.' + parts[2].replace('.', '')

  workgroup = os.path.join(softimage_workgroup_root, 'renderer', 'RedShift', version)
  if not os.path.exists(workgroup):
    os.makedirs(workgroup)
  else:
    QtGui.QMessageBox.critical(None, "ZooKeeper Error", "The folder\n\n%s\n\nalready exists. Please remove it first and restart this utility." % workgroup)
    return False

  print 'Unzipping %s ....' % zipFile
  with zipfile.ZipFile(zipFile, "r") as z:
    z.extractall(os.path.join(workgroup))

  # setup the preferences
  template = """
  <?xml version=\"1.0\" encoding=\"UTF-8\"?>
  <redshift_preferences version=\"1.2\">
    <preference name=\"CacheFolder\" type=\"string\" value=\"%ZK_PROJECT_SCRATCH_FOLDER%\\Redshift\\Cache\\\" />
    <preference name=\"TextureCacheBudgetGB\" type=\"int\" value=\"64\" />
  </redshift_preferences>
  """
  # <preference name="AllCudaDevices" type="string" value="0:Quadro K6000," />
  # <preference name="SelectedCudaDevices" type="string" value="0:Quadro K6000," />
  preferencesPath = os.path.join(workgroup, 'Preferences')
  if not os.path.exists(preferencesPath):
    os.makedirs(preferencesPath)
  xmlPath = os.path.join(preferencesPath, 'preferences.xml')
  open(xmlPath, 'w').write(template)

  extractTool = os.path.join(softimage_workgroup_root, 'util', 'xsiaddonExtractor.exe')

  addonFiles = glob.glob(os.path.join(workgroup, 'Redshift', 'Plugins', 'Softimage', '*.xsiaddon'))
  for addonFile in addonFiles:
    softimageVersions = [addonFile.lower().rpartition('softimage')[2].partition('.')[0].upper()]
    if softimageVersions[0] == '2014SP2':
      softimageVersions += ['2015SP2']

    for softimageVersion in softimageVersions:
      addonPath = os.path.join(workgroup, 'Softimage'+softimageVersion)
      cmd = [extractTool, '-o', addonPath, addonFile]
      process = subprocess.Popen(cmd)
      process.wait()

      # hmathee: don't create the pathconfig files anymore - we are not using them
      # xmlPath = os.path.join(addonPath, 'Application', 'Plugins', 'bin', 'nt-x86-64', 'pathconfig.xml')
      # template = "<path name=\"REDSHIFT_COREDATAPATH\" value=\"%s\" />\n"
      # template += "<path name=\"REDSHIFT_PREFSPATH\" value=\"%s\" />\n"
      # xmlContent = template % (
      #   "%ZK_SOFTIMAGE_WORKGROUP_ROOT%/renderer/RedShift/%ZK_RENDERER_VERSION%/RedShift",
      #   "%ZK_SOFTIMAGE_WORKGROUP_ROOT%/renderer/RedShift/%ZK_RENDERER_VERSION%/Preferences/preferences.xml")
      # open(xmlPath,'w').write(xmlContent)

  print '\nInstalled to '+workgroup

  return True

def main():

  # instantiate the qt app
  app = zookeeper.zkUI.zkApp()

  conn = zookeeper.zkDB.zkConnection(debug = False)

  softimage_workgroup_root = zookeeper.zkDB.zkSetting.getByName(conn, 'softimage_workgroup_root').value
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
    result = installRedShiftZip(softimage_workgroup_root, fields[0]['value'])
    msgBox.close()
    if result:
      QtGui.QMessageBox.information(None, "ZooKeeper", "Successfully installed.")

  dialog = zookeeper.zkUI.zkFieldsDialog(fields, onAccepted, None)
  dialog.exec_()

main()
