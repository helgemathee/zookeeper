import platform
import socket
import multiprocessing
import psutil

import zookeeper
import zookeeper.zkDB
from zookeeper.zkConfig_impl import zkConfig
from zkEntity_impl import zkEntity

class zkMemberShip(zkEntity):

  def __init__(self, connection, id = None):
    super(zkMemberShip, self).__init__(connection, table = 'membership', id = id)
