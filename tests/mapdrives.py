import zookeeper

conn = zookeeper.zkDB.zkConnection()

def log(message):
  print message

job = zookeeper.zkDB.zkJob.getById(conn, 829)

zookeeper.zk_mapNetworkDrivesForJob(conn, job, logCallback = log)
