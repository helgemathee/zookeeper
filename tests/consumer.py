import zookeeper

conn = zookeeper.zkDB.zkConnection()
# conn.setDebug(True)

app = zookeeper.zkUI.zkApp()
consumer = zookeeper.zkClient.zkConsumer(conn)
app.exec_()
