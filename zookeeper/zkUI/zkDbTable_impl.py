import os
import time
from PySide import QtCore, QtGui
from zkDbTableModel_impl import zkDbTableModel

class zkDbTable(QtGui.QTableView):

  __model = None
  __percentages = None

  contextMenuRequested = QtCore.Signal(list, str)

  def __init__(self, conn, itemCls, procedure = None, procedureArgs = None, labels = None, widths = None, getItemDataCallback = None, parent = None):

    super(zkDbTable, self).__init__(parent)

    if widths:
      if len(widths) == len(labels):
        total = 0.0
        for width in widths:
          total += float(width)
        if total > 0:
          self.__percentages = []
          for width in widths:
            self.__percentages += [float(width) / total]
    if not self.__percentages:
      self.__percentages = []
      for label in labels:
        self.__percentages += [1.0 / float(len(labels))]

    self.setStyleSheet("QTableWidget::item { padding: 0px }")
    self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)

    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    self.verticalHeader().hide()

    self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.onContextMenuRequested);

    self.__model = zkDbTableModel(self, conn, itemCls, procedure, procedureArgs, labels, getItemDataCallback)
    self.setModel(self.__model)

  def resizeEvent(self, event):
    if not self.__percentages:
      return
    width = event.size().width()
    for i in range(len(self.__percentages)):
      self.setColumnWidth(i, width * self.__percentages[i])

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
