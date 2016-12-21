import zookeeper

conn = zookeeper.zkDB.zkConnection(debug=False)
app = zookeeper.zkUI.zkApp()
consumer = zookeeper.zkClient.zkConsumer(conn)
app.exec_()
