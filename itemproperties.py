from PyQt4.QtCore import *
from PyQt4.QtGui import *

from model import *

class ItemPropertiesWidget(QWidget):
  def __init__(self, scene, parent = None):
    QWidget.__init__(self, parent)
    self.scene = scene
    self.connect(self.scene, SIGNAL("selectionChanged()"), self.sceneSelectionChanged)

  def sceneSelectionChanged(self):
    sel = self.scene.selectedItems()
    if not sel:
      return
    
    sel = sel[0]
    print "selection changed", sel