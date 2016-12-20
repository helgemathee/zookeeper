import zookeeper

conn = zookeeper.zkDB.zkConnection(debug=True)
app = zookeeper.zkUI.zkApp()
consumer = zookeeper.zkClient.zkConsumer(conn)
app.exec_()
