import zookeeper
import win32com.client
from win32com.client import constants

def XSILoadPlugin( in_reg ):
  in_reg.Author = "Helge Mathee"
  in_reg.Name = "ZooKeeperPlugin"
  in_reg.Major = 1
  in_reg.Minor = 0

  in_reg.RegisterCommand("zkSubmit","zkSubmit")
  in_reg.RegisterCommand("zkShowManager","zkShowManager")
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
  consumer.setModal(True)
  app.exec_()
  return True

def ZooKeeper_Init( in_ctxt ):
  oMenu = in_ctxt.Source
  oMenu.AddCommandItem("ZooKeeper Submit","zkSubmit")
  oMenu.AddSeparatorItem()
  oMenu.AddCommandItem("ZooKeeper Manager","zkShowManager")
  return True
