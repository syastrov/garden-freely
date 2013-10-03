#!/usr/bin/env python

"""
  Garden Freely: Garden design and planning software
  Copyright (C) 2008 Seth Yastrov <syastrov@gmail.com>

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 3
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

import sys

from ui_mainwindow import Ui_MainWindow

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from model import *
from plantdblistview import *
from gardenproperties import *
from itemproperties import *

class MainWindow(QMainWindow):
  def __init__(self, parent = None):
    QWidget.__init__(self, parent)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.garden = Garden()
    self.gardenScene = self.ui.gardenView.scene()
    self.gardenScene.setGarden(self.garden)
    
    self.setCurrentFile("")

    self.connectSignalsSlots()
    self.createToolToolBar()
    self.createDockWidgets()
    self.createUndoRedoGroups()

    self.gardenPropertiesDialog = GardenPropertiesDialog(self.garden, self)

    if len(sys.argv) > 1:
      self.loadFile(sys.argv[1])

  def connectSignalsSlots(self):
    self.connect(self.ui.action_Quit, SIGNAL("triggered()"), self.close)
    self.connect(self.ui.action_New, SIGNAL("triggered()"), self.newFile)
    self.connect(self.ui.action_Open, SIGNAL("triggered()"), self.openFile)
    
    self.connect(self.ui.action_Save, SIGNAL("triggered()"), self.save)
    self.connect(self.ui.action_Save_As, SIGNAL("triggered()"), self.saveAs)
    
    self.connect(self.ui.action_Print, SIGNAL("triggered()"), self.printScene)

    self.connect(self.ui.action_Garden_Properties, SIGNAL("triggered()"), self.showGardenProperties)
    
    self.connect(self.ui.action_Delete, SIGNAL("triggered()"), self.delete)
    self.connect(self.ui.action_Select_All, SIGNAL("triggered()"), self.selectAll)
    self.connect(self.ui.action_Select_None, SIGNAL("triggered()"), self.selectNone)


  def createToolToolBar(self):
    self.ui.toolToolBar = QToolBar(self)
    self.ui.toolToolBar.setAllowedAreas(Qt.AllToolBarAreas)
    self.ui.toolToolBar.setObjectName("toolToolBar")
    self.addToolBar(Qt.LeftToolBarArea, self.ui.toolToolBar)

    self.toolGroup = QActionGroup(self)
    self.toolGroup.addAction(self.ui.action_Rectangular_Selection)
    self.toolGroup.addAction(self.ui.action_Place_Plant)
    self.toolGroup.addAction(self.ui.action_Plant_Row)
    self.toolGroup.addAction(self.ui.action_Plant_Bed)
    self.toolGroup.addAction(self.ui.action_Ruler)
    self.ui.action_Place_Plant.setChecked(True)

    self.ui.toolToolBar.addActions(self.toolGroup.actions())

    self.connect(self.toolGroup, SIGNAL("triggered(QAction*)"), self.changeTool)

  def createDockWidgets(self):
    # Plant Database
    
    self.ui.dockWidget = QDockWidget(self.tr("Plant Database"), self)

    self.ui.plantDBListView = PlantDBListView(self.ui.dockWidget)
    self.connect(self.ui.plantDBListView, SIGNAL("plantFactoryActivated"), self.plantFactoryActivated)

    # Select first one by default
    self.ui.plantDBListView.setCurrentIndex(self.ui.plantDBListView.model().createIndex(0, 0))
    
    self.ui.dockWidget.setWidget(self.ui.plantDBListView)
    self.addDockWidget(Qt.RightDockWidgetArea, self.ui.dockWidget)


    # Item Properties
    
    self.ui.propertiesDock = QDockWidget(self.tr("Properties"), self)

    self.ui.propertiesWidget = ItemPropertiesWidget(self.gardenScene, self.ui.propertiesDock)
    
    self.ui.propertiesDock.setWidget(self.ui.propertiesWidget)
    self.addDockWidget(Qt.RightDockWidgetArea, self.ui.propertiesDock)


  def createUndoRedoGroups(self):
    self.undoGroup = QUndoGroup(self)

    self.connect(self.undoGroup, SIGNAL("cleanChanged(bool)"), self.cleanChanged)

    undoAction = self.undoGroup.createUndoAction(self)
    undoAction.setIcon(QIcon(":/images/undo.png"))
    redoAction = self.undoGroup.createRedoAction(self)
    redoAction.setIcon(QIcon(":/images/redo.png"))

    undoAction.setShortcut(QApplication.translate("MainWindow", "Ctrl+Z", None, QApplication.UnicodeUTF8))
    redoAction.setShortcut(QApplication.translate("MainWindow", "Ctrl+Shift+Z", None, QApplication.UnicodeUTF8))
    
    self.ui.menu_Edit.insertActions(self.ui.menu_Edit.actions()[0], [undoAction, redoAction])

    self.ui.toolBar.addAction(undoAction)
    self.ui.toolBar.addAction(redoAction)

    self.undoGroup.addStack(self.gardenScene.undoStack)
    self.undoGroup.setActiveStack(self.gardenScene.undoStack)


  def plantFactoryActivated(self, plantFactory):
    self.gardenScene.setPlantFactory(plantFactory)

  def changeTool(self, action):
    if action.objectName() == "action_Rectangular_Selection":
      tool = "RectangularSelection"
    elif action.objectName() == "action_Place_Plant":
      tool = "PlacePlant"
    elif action.objectName() == "action_Plant_Row":
      tool = "PlantRow"
    elif action.objectName() == "action_Plant_Bed":
      tool = "PlantBed"
    elif action.objectName() == "action_Ruler":
      tool = "Ruler"
    
    self.gardenScene.setTool(tool)

  def closeEvent(self, event):
    if self.maybeSave():
      self.gardenPropertiesDialog.close()
      event.accept()
    else:
      event.ignore()

  def newFile(self):
    if self.maybeSave():
      self.setCurrentFile("")
      self.undoGroup.activeStack().clear()
      self.garden.clear()

  def save(self):
    if not self.curFile:
      return self.saveAs()
    else:
      return self.saveFile(self.curFile)

  def saveAs(self):
    fileName = QFileDialog.getSaveFileName(self,
      self.tr("Save Garden"), "", self.tr("Garden Files (*.garden)"))
    if not fileName:
      return False

    return self.saveFile(fileName)

  def openFile(self):
    if self.maybeSave():
      fileName = QFileDialog.getOpenFileName(self,
        self.tr("Open Garden"), "", self.tr("Garden Files (*.garden)"))
      if not fileName:
        return False

      return self.loadFile(str(fileName))

  def loadFile(self, fileName):
    self.setCurrentFile(fileName)
    self.undoGroup.activeStack().clear()
    return self.garden.load(str(fileName))

  def saveFile(self, fileName):
    self.setCurrentFile(fileName)
    self.garden.save(fileName)
    self.undoGroup.activeStack().setClean()

  def cleanChanged(self, isClean):
    self.setWindowModified(not isClean)

  def setCurrentFile(self, fileName):
    self.curFile = fileName
    self.setWindowModified(False)

    if not self.curFile:
      shownName = "untitled.garden"
    else:
      shownName = QFileInfo(self.curFile).fileName()

    self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(self.tr("Garden Freely")));

  def maybeSave(self):
    if not self.undoGroup.isClean():
      ret = QMessageBox.warning(self, self.tr("Garden Freely"),
              self.tr("The document has been modified.\n"
                      "Do you want to save your changes?"),
              QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
      if ret == QMessageBox.Save:
        return self.save()
      elif ret == QMessageBox.Cancel:
        return False
      
    return True


  def printScene(self):
    printer = QPrinter()
    if QPrintDialog(printer).exec_() == QDialog.Accepted:
      painter = QPainter(printer)
      painter.printing = True
      painter.setRenderHint(QPainter.Antialiasing)
      self.gardenScene.render(painter)
      painter.end()

  def selectAll(self):
    for item in self.gardenScene.items():
      item.setSelected(True)

  def selectNone(self):
    self.gardenScene.clearSelection()

  def delete(self):
    self.gardenScene.deleteAction()

  def showGardenProperties(self):
    self.gardenPropertiesDialog.show()

  def on_action_Show_Plant_Spacing_toggled(self, checked):
    self.gardenScene.setShowPlantSpacing(checked)

  def on_action_Show_Row_Spacing_toggled(self, checked):
    self.gardenScene.setShowRowSpacing(checked)
    

def main():
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec_())

if __name__ == "__main__":
  # Import Psyco if available
  #try:
    #import psyco
    #psyco.full()
  #except ImportError:
    #pass

  main()