import zookeeper

conn = zookeeper.zkDB.zkConnection()
# conn.setDebug(True)

app = zookeeper.zkUI.zkApp()
manager = zookeeper.zkClient.zkManager(conn)
app.exec_()
