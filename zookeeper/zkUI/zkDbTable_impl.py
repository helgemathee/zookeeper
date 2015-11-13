import os
from PySide import QtCore, QtGui

class zkDbTable(QtGui.QTableWidget):

  __conn = None
  __itemCls = None
  __procedure = None
  __procedureArgs = None
  __labels = None
  __createItemCallback = None
  __fillItemCallback = None
  __polling = None
  __labelsSet = None

  contextMenuRequested = QtCore.Signal(int, str)

  def __init__(self, conn, itemCls, procedure = None, procedureArgs = None, labels = None, createItemCallback = None, fillItemCallback = None, parent = None):

    self.__conn = conn
    self.__itemCls = itemCls
    self.__labels = labels
    self.__createItemCallback = createItemCallback
    self.__fillItemCallback = fillItemCallback    
    self.__polling = False
    self.__labelsSet = False

    super(zkDbTable, self).__init__(parent)

    self.setStyleSheet("QTableWidget::item { padding: 0px }")
    self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    self.verticalHeader().hide()

    self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.onContextMenuRequested);
    self.setProcedure(procedure, procedureArgs) # also polls

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

    data = self.__conn.call(self.__procedure, self.__procedureArgs)

    vHeader = self.verticalHeader()
    vHeader.setResizeMode(QtGui.QHeaderView.ResizeToContents)

    numRows = len(data)
    numCols = 0
    if numRows > 0:
      numCols = len(data[0])

    if self.rowCount() > numRows or self.columnCount() > numCols:
      self.clear()
      self.setRowCount( 0);
      self.__labelsSet = False

    while self.columnCount() < numCols:
      self.insertColumn(self.columnCount())
    while self.rowCount() < numRows:
      self.insertRow(self.rowCount())

    if not self.__labelsSet and numCols > 0:
      # top labels 
      if self.__labels:
        self.setHorizontalHeaderLabels(self.__labels)
      else:
        for j in range(len(labels)):
          labels[j] = labels[j].rpartition('_')[2]
        self.setHorizontalHeaderLabels(labels)
      self.__labelsSet = True

    for i in range(len(data)):
      for j in range(len(data[i])):
        item = self.item(i, j)
        caption = self.horizontalHeaderItem(j).text()
        if not item:
          if self.__createItemCallback:
            item = self.__createItemCallback(self, data[i][0], caption, data[i][j])
          if not item:
            item = QtGui.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
          self.setItem(i, j, item)

        if self.__fillItemCallback:
          if self.__fillItemCallback(self, item, data[i][0], caption, data[i][j]):
            continue
        item.setText(str(data[i][j]))

    self.__polling = False

  def onContextMenuRequested(self, point):
    item = self.itemAt(point)
    if not item:
      return
    id = int(self.item(item.row(), 0).text())
    caption = self.horizontalHeaderItem(item.column()).text()
    self.contextMenuRequested.emit(id, caption)
