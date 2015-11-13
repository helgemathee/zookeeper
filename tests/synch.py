import zookeeper

a = 'c:\\temp'
b = 'f:\\temp'

files = zookeeper.zkClient.zk_findFiles("c:\\temp")
files += zookeeper.zkClient.zk_findFiles("E:\\video\\capture")
files += zookeeper.zkClient.zk_findFiles("\\\\domain\\public\\workshop")

zookeeper.zkClient.zk_synchronizeFilesBetweenFolders(files, a, b)
