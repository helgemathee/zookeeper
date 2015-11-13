import zookeeper



cfg = zookeeper.zkConfig()
cfg.set('gpuramgb', 12)

# env = zookeeper.zkClient.getSoftimageEnv(cfg, '2014 SP2')

# for key in env:
#   print key + ' = ' + env[key]

# zk_synchronizeFolder('c:\\temp\\zookeeper', "c:\\temp\\test")

# a = 'c:\\temp\\homefront'
# b = '\\\\domain\\public\\homefront'

# filesToSync = [
#   "c:\\temp\\homefront\\projects\\projectA\\Scenes\\a.scn",
#   "c:\\temp\\homefront\\projects\\projectA\\Pictures\\a.gif",
#   "d:\\temp\\homefront\\assets\\Textures\\a.gif",
#   "\\\\mystorage\\share\\texture\\Pictures\\c.gif",
#   ]

# for p in filesToSync:
#   print p

# print '-------'

# for p in filesToSync:
#   print zk_createSynchronizeTargetPath(a, b, p)
