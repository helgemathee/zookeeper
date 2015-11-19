import os
import time
from PySide import QtCore, QtGui

class zkDbTableModel(QtCore.QAbstractTableModel):

  __table = None
  __conn = None
  __itemCls = None
  __getItemDataCallback = None
  __polling = None
  __labels = None
  __data = None
  __procedure = None
  __procedureArgs = None

  def __init__(self, table, conn, itemCls, procedure = None, procedureArgs = None, labels = None, getItemDataCallback = None):

    self.__table = table
    self.__conn = conn
    self.__itemCls = itemCls
    self.__getItemDataCallback = getItemDataCallback    
    self.__polling = False
    self.__labels = labels
    self.__data = []

    super(zkDbTableModel, self).__init__(table)

    self.setProcedure(procedure, procedureArgs) # also polls

  def rowCount(self, parent = QtCore.QModelIndex()):
    return len(self.__data)

  def columnCount(self, parent = QtCore.QModelIndex()):
    if self.rowCount() == 0:
      return 0
    if parent.isValid():
      return 1
    return len(self.__data[0])

  def data(self, index, role = QtCore.Qt.DisplayRole):
    if role == QtCore.Qt.TextAlignmentRole:
      return QtCore.Qt.AlignCenter

    if not role in [QtCore.Qt.DisplayRole, QtCore.Qt.BackgroundRole]:
      return None

    result = self.__data[index.row()][index.column()]
    if index.column() > 0 and self.__getItemDataCallback:
      id = self.__data[index.row()][0]
      result = self.__getItemDataCallback(self.__table, self.__labels[index.column()], id, result, role)
    return result

  def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
    if role == QtCore.Qt.DisplayRole:
      if orientation == QtCore.Qt.Orientation.Vertical:
        return str(section)
      return self.__labels[section]
    return None

  def getIdFromIndex(self, index):
    return self.__data[index.row()][0]

  def setProcedure(self, procedure, procedureArgs = None):
    self.__procedure = procedure
    if procedureArgs:
      self.__procedureArgs = procedureArgs
    else:
      self.__procedureArgs = []
    self.poll()

  def setProcedureArgs(self, procedureArgs):
    if procedureArgs:
      self.__procedureArgs = procedureArgs
    else:
      self.__procedureArgs = []
    self.poll()

  def poll(self):
    if not self.__procedure:
      return
    if self.__polling:
      return
    self.__polling = True

    prevRowCount = self.rowCount()
    self.__data = self.__conn.call(self.__procedure, self.__procedureArgs)

    if self.rowCount() == prevRowCount:
      if self.rowCount() > 0:
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount()-1, self.columnCount()-1))
    else:
      self.modelReset.emit()

    self.__polling = False

