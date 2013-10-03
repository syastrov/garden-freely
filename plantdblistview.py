from PyQt4.QtCore import *
from PyQt4.QtGui import *

from model import *

class PlantDBListModel(QAbstractListModel):
  def __init__(self, plantDB, parent = None):
    QAbstractListModel.__init__(self, parent)
    self.plantDB = plantDB

  def data(self, index, role):
    if not index.isValid():
      return QVariant()

    if index.row() >= len(self.plantDB):
      return QVariant()

    plantFactory = self.plantDB.plantFactoryAt(index.row())
  
    if role == Qt.DisplayRole:
      return QVariant(plantFactory.species)
    elif role == Qt.DecorationRole:
      return QVariant(QIcon(plantFactory.icon))
    else:
      return QVariant()

  def plantFactoryAt(self, index):
    if not index.isValid or index.row() >= len(self.plantDB):
      return None
    return self.plantDB.plantFactoryAt(index.row())
  
  def rowCount(self, parent):
    if parent.isValid():
      return 0
    else:
      return len(self.plantDB)


class PlantDBListView(QListView):
  def __init__(self, parent = None):
    QListView.__init__(self, parent)
    self.setModel(PlantDBListModel(PlantDB, self))
    self.setViewMode(self.IconMode)
    self.setGridSize(QSize(70, 70))

  def currentChanged(self, current, previous):
    self.emit(SIGNAL("plantFactoryActivated"), self.model().plantFactoryAt(current))
    