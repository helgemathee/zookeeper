import os
import sys
import zookeeper
import win32com.client
from win32com.client import constants
from PySide import QtCore, QtGui

def XSILoadPlugin( in_reg ):
  in_reg.Author = "Helge Mathee"
  in_reg.Name = "ZooKeeperPlugin"
  in_reg.Major = 1
  in_reg.Minor = 0

  in_reg.RegisterCommand("zkSubmit","zkSubmit")
  in_reg.RegisterCommand("zkShowManager","zkShowManager")
  in_reg.RegisterCommand("zkSynchSceneToNetwork","zkSynchSceneToNetwork")
  in_reg.RegisterMenu(constants.siMenuMainTopLevelID,"ZooKeeper",False,False)

  return True

def XSIUnloadPlugin( in_reg ):
  strPluginName = in_reg.Name
  Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
  return True

def zkSubmit_Init( in_ctxt ):
  oCmd = in_ctxt.Source
  oCmd.Description = ""
  oCmd.ReturnValue = True
  return True

def zkSubmit_Execute(  ):
  conn = zookeeper.zkDB.zkConnection(debug = True)
  submitter = zookeeper.zkClient.zkSoftimageSubmitter(conn, Application, constants)
  submitter.submitWithDialog()
  return True

def zkShowManager_Init( in_ctxt ):
  oCmd = in_ctxt.Source
  oCmd.Description = ""
  oCmd.ReturnValue = True
  return True

def zkShowManager_Execute(  ):
  conn = zookeeper.zkDB.zkConnection(debug = False)
  app = zookeeper.zkUI.zkApp()
  consumer = zookeeper.zkClient.zkManager(conn)
  app.exec_()
  return True

def zkSynchSceneToNetwork_Init( in_ctxt ):
  oCmd = in_ctxt.Source
  oCmd.Description = ""
  oCmd.ReturnValue = True
  return True

def zkSynchSceneToNetwork_Execute(  ):
  app = zookeeper.zkUI.zkApp()

  projectPath = Application.ActiveProject.Path
  sourceFolder = projectPath

  # build up the UI
  fields = []
  fields += [{'name': 'sourceProject', 'value': sourceFolder, 'type': 'folder', 'tooltip': 'The source project for the sync.', 'readonly': True}]
  fields += [{'name': 'targetProject', 'value': '', 'type': 'folder', 'tooltip': 'The target project for the sync.'}]
  fields += [{'name': 'createProject', 'value': False, 'type': 'bool', 'tooltip': 'If checked a project will be created in the targetProject location.'}]
  fields += [{'name': 'sourceFolder', 'value': '', 'type': 'folder', 'tooltip': 'OPTIONAL: The source folder for the sync. Can be the project folder or levels higher up.'}]
  fields += [{'name': 'targetFolder', 'value': '', 'type': 'folder', 'tooltip': 'OPTIONAL: The target folder for the sync. Can be the network folder or levels higher up.'}]

  hook = zookeeper.zkClient.zkSoftimageLogHook(Application)
  sys.stdout = hook
  sys.stderr = hook

  def onAccepted(fields):
    scene = Application.ActiveProject.ActiveScene
    scenePathName = str(scene.FileName.Value)
    externalFiles = scene.ExternalFiles
    pathsToSynch = []
    pathsToAdapt = []
    pathsHit = {}
    for i in range(externalFiles.Count):
      externalFile = externalFiles(i)
      resolvedPath = externalFile.ResolvedPath
      if pathsHit.has_key(resolvedPath):
        index = pathsHit[resolvedPath]
        pathsToAdapt[index] += [{'obj': externalFile, 'type': 'ExternalFile'}]
        continue
      pathsHit[resolvedPath] = len(pathsToSynch)
      pathsToSynch += [resolvedPath]
      pathsToAdapt += [[{'obj': externalFile, 'type': 'ExternalFile'}]]

    # here you can add additional files, they need to be added in the format of
    # pathsToSynch += [resolvedPathOnDisc]
    # pathsToAdapt += [[{'obj': xsiObjectToUpdate, 'type': 'MyType'}]]

    sourceProject = fields[0]['value']
    targetProject = fields[1]['value']
    createProject = fields[2]['value']
    sourceFolder = fields[3]['value']
    targetFolder = fields[4]['value']

    if targetProject == '':
      QtGui.QMessageBox.warning(None, 'ZooKeeper Warning', 'No target project specified.')
      return False

    if sourceFolder == '':
      sourceFolder = sourceProject
    if targetFolder == '':
      targetFolder = targetProject

    if createProject:
      Application.ActiveProject2 = Application.CreateProject2(targetProject)

    synchedPaths = zookeeper.zkClient.zk_synchronizeFilesBetweenFolders(pathsToSynch, sourceFolder, targetFolder)
    for i in range(len(pathsToAdapt)):
      if synchedPaths[i] is None:
        continue
      for pathToAdapt in pathsToAdapt[i]:

        if pathToAdapt['type'] == 'ExternalFile':

          pathToAdapt['obj'].Path = synchedPaths[i]

        # here you can add other cases for your own file object types
        # elif pathToAdapt['type'] == 'MyType':
        #   pathToAdapt['obj'].filePathParam.Value = synchedPaths[i]

    relScenePath = os.path.relpath(scenePathName, sourceProject)
    Application.SaveSceneAs(os.path.join(targetProject, relScenePath))

    message = "The scene is now in the target location. It has been saved as\n\n"
    message += os.path.normpath(os.path.join(targetProject, relScenePath))
    message += "\n\nYou can submit this scene for rendering now."
    QtGui.QMessageBox.information(None, 'ZooKeeper', message)

  dialog = zookeeper.zkUI.zkFieldsDialog(fields, onAcceptedCallback = onAccepted, onRejectedCallback = None)
  dialog.setMinimumWidth(600)
  dialog.exec_()

  return True

def ZooKeeper_Init( in_ctxt ):
  oMenu = in_ctxt.Source
  oMenu.AddCommandItem("ZooKeeper Submit","zkSubmit")
  oMenu.AddSeparatorItem()
  oMenu.AddCommandItem("ZooKeeper Manager","zkShowManager")
  oMenu.AddSeparatorItem()
  oMenu.AddCommandItem("Synch Scene to Network","zkSynchSceneToNetwork")
  return True
