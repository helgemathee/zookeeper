import zookeeper

conn = zookeeper.zkDB.zkConnection()
app = zookeeper.zkUI.zkApp()
consumer = zookeeper.zkClient.zkConsumer(conn)
app.exec_()
