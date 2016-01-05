import os
import time
from PySide import QtCore, QtGui
from zkDbTableModel_impl import zkDbTableModel

class zkDbTable(QtGui.QTableView):

  __model = None

  contextMenuRequested = QtCore.Signal(list, str)

  def __init__(self, conn, itemCls, procedure = None, procedureArgs = None, labels = None, getItemDataCallback = None, parent = None):

    super(zkDbTable, self).__init__(parent)

    self.setStyleSheet("QTableWidget::item { padding: 0px }")
    self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    self.verticalHeader().hide()

    self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.onContextMenuRequested);

    self.__model = zkDbTableModel(self, conn, itemCls, procedure, procedureArgs, labels, getItemDataCallback)
    self.setModel(self.__model)

  def onContextMenuRequested(self, point):
    indices = self.selectedIndexes()
    if not indices:
      return
    ids = []
    for index in indices:
      if not index.isValid:
        continue
      id = int(self.__model.getIdFromIndex(index))
      ids += [id]
      caption = self.__model.headerData(index.column(), QtCore.Qt.Orientation.Horizontal)
    self.contextMenuRequested.emit(ids, caption)

  def pollOnModel(self):
    indices = self.selectedIndexes()
    self.__model.poll()
    if indices:
      for i in range(len(indices)):
        self.selectionModel().select(indices[i], QtGui.QItemSelectionModel.Select)
