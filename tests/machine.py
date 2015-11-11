from zookeeper import *

conn = zkConnection()
conn.setDebug(True)

machine = zkMachine(conn, asClient = True)
