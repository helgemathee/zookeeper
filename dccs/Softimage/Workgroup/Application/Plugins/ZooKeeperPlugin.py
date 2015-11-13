import zookeeper
import win32com.client
from win32com.client import constants

null = None
false = 0
true = 1

def XSILoadPlugin( in_reg ):
  in_reg.Author = "Helge Mathee"
  in_reg.Name = "ZooKeeperPlugin"
  in_reg.Major = 1
  in_reg.Minor = 0

  in_reg.RegisterCommand("zkSubmit","zkSubmit")
  in_reg.RegisterMenu(constants.siMenuMainTopLevelID,"ZooKeeper",false,false)

  return true

def XSIUnloadPlugin( in_reg ):
  strPluginName = in_reg.Name
  Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
  return true

def zkSubmit_Init( in_ctxt ):
  oCmd = in_ctxt.Source
  oCmd.Description = ""
  oCmd.ReturnValue = true
  return true

def zkSubmit_Execute(  ):
  conn = zookeeper.zkDB.zkConnection()
  submitter = zookeeper.zkClient.zkSoftimageSubmitter(conn, Application, constants)
  submitter.submitWithDialog()
  return true

def ZooKeeper_Init( in_ctxt ):
  oMenu = in_ctxt.Source
  # oMenu.AddSeparatorItem()
  oMenu.AddCommandItem("ZooKeeper Submit","zkSubmit")
  return true

