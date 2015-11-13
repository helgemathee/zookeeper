import zookeeper

conn = zookeeper.zkDB.zkConnection()
app = zookeeper.zkUI.zkApp()
consumer = zookeeper.zkClient.zkManager(conn)
app.exec_()
