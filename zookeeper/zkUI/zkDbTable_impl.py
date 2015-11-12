import os
from PySide import QtCore, QtGui

class zkDbTable(QtGui.QTableWidget):

  __conn = None
  __itemCls = None
  __query = None
  __labels = None
  __createItemCallback = None
  __fillItemCallback = None

  contextMenuRequested = QtCore.Signal(int, str)

  def __init__(self, conn, itemCls, query = None, labels = None, createItemCallback = None, fillItemCallback = None, parent = None):

    self.__conn = conn
    self.__itemCls = itemCls
    self.__query = query
    self.__labels = labels
    self.__createItemCallback = createItemCallback
    self.__fillItemCallback = fillItemCallback    

    super(zkDbTable, self).__init__(parent)

    self.setStyleSheet("QTableWidget::item { padding: 0px }");

    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    self.verticalHeader().hide()
    self.poll()

    self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.onContextMenuRequested);

  def setQuery(self, query):
    self.__query = query
    self.poll()

  def poll(self):
    if self.__query:
      self.fillFromQuery()
    else:
      self.fillFromItemCls()

  def fillFromQuery(self, query = None, labels = None):
    if query:
      self.__query = query

    data = self.__conn.execute(self.__query)

    vHeader = self.verticalHeader()
    vHeader.setResizeMode(QtGui.QHeaderView.ResizeToContents)

    numRows = len(data)
    numCols = 0
    if numRows > 0:
      numCols = len(data[0])

    if not self.rowCount() == numRows or not self.columnCount() == numCols:
      self.clear()
      self.clearContents()
      for i in range(len(data)):
        if i == 0:
          for j in range(len(data[0])):
            self.insertColumn(j)
          # top labels 
          if self.__labels:
            self.setHorizontalHeaderLabels(self.__labels)
          else:
            for j in range(len(labels)):
              labels[j] = labels[j].rpartition('_')[2]
            self.setHorizontalHeaderLabels(labels)
        self.insertRow(i)

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

  def fillFromItemCls(self):
    table = self.__itemCls.getTableName()
    fields = self.__itemCls.getUIFields(self.__conn)
    orderField = self.__itemCls.getMainOrderField()
    query = 'SELECT %s FROM %s ORDER BY %s ASC' % (','.join(fields), table, orderField)
    self.fillFromQuery(query, fields)

  def onContextMenuRequested(self, point):
    item = self.itemAt(point)
    if not item:
      return
    id = int(self.item(item.row(), 0).text())
    caption = self.horizontalHeaderItem(item.column()).text()
    self.contextMenuRequested.emit(id, caption)
