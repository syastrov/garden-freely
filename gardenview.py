import sys
import math
from model import *
from commands import *

from PyQt4.QtCore import *

from PyQt4.QtGui import *

ENABLE_OPENGL = False

if ENABLE_OPENGL:
  from PyQt4.QtOpenGL import *

class GardenScene(QGraphicsScene):
  def __init__(self, parent):
    QGraphicsScene.__init__(self, parent)
    self.undoStack = QUndoStack(self)
    self.tool = "PlacePlant"
    self.gridPen = QPen(QColor(0, 82, 230), 0, Qt.SolidLine)
    self.gridPen.setCosmetic(True)

    self.showPlantSpacing = True
    self.showRowSpacing = True
    #self.setSceneRect(-sys.maxint/2, -sys.maxint/2, sys.maxint, sys.maxint)

  def setGarden(self, garden):
    self.garden = garden
    self.connect(self.garden, SIGNAL("loaded"), self.loadGarden)
    self.connect(self.garden, SIGNAL("cleared"), self.clear)
    self.connect(self.garden, SIGNAL("objectAdded"), self.addObject)
    self.connect(self.garden, SIGNAL("objectRemoved"), self.removeObject)
    self.connect(self.garden, SIGNAL("backgroundImageSet"), self.backgroundImageSet)
    self.connect(self.garden, SIGNAL("backgroundImageScaleSet"), self.backgroundImageScaleSet)
    self.connect(self.garden, SIGNAL("backgroundOpacitySet"), self.backgroundOpacitySet)

  def topLevelItems(self):
    items = []
    for item in self.items():
      if not item.parentItem():
        items.append(item)
    return items

  def clear(self):
    for item in self.topLevelItems():
      self.removeItem(item)

  def loadGarden(self):
    for p in self.garden.objects:
      self.addObject(p)

  def addObject(self, p):
    item = p.createGraphicsItem()
    self.addItem(item)

  def removeObject(self, p):
    for item in self.items():
      if hasattr(item, "gardenObject") and item.gardenObject == p:
        self.removeItem(item)

  def backgroundImageSet(self, backgroundImage):
    if not backgroundImage:
      self.setBackgroundBrush(QBrush())
      return
    img = QImage(backgroundImage)
    if img:
      img = img.scaled(img.size() * self.garden.backgroundImageScale)
      alpha = img.alphaChannel()
      alpha.fill(int(self.garden.backgroundOpacity*255))
      img.setAlphaChannel(alpha)
      brush = QBrush(img)
      self.setBackgroundBrush(brush)

  def backgroundImageScaleSet(self, scale):
    if self.garden.backgroundImage:
      self.backgroundImageSet(self.garden.backgroundImage)

  def backgroundOpacitySet(self, opacity):
    if self.garden.backgroundImage:
      self.backgroundImageSet(self.garden.backgroundImage)


  def deleteAction(self):
    """Deletes currently selected items"""
    itemsToRemove = []
    for item in self.selectedItems():
      itemsToRemove.append(item.gardenObject)
    self.undoStack.push(CmdRemoveObjects(self.garden, itemsToRemove))


  def setPlantFactory(self, plantFactory):
    self.plantFactory = plantFactory

  def setTool(self, tool):
    self.tool = tool
    if tool == "RectangularSelection":
      for view in self.views():
        view.setDragMode(view.RubberBandDrag)
    else:
      for view in self.views():
        view.setDragMode(view.NoDrag)

  def setShowPlantSpacing(self, showPlantSpacing):
    self.showPlantSpacing = showPlantSpacing
    self.update()

  def setShowRowSpacing(self, showRowSpacing):
    self.showRowSpacing = showRowSpacing
    self.update()
  
  def mousePressEvent(self, event):
    QGraphicsScene.mousePressEvent(self, event)
    
    if event.button() != Qt.LeftButton:
      return
    pos = event.scenePos()

    self.oldPos = pos

    if self.tool == "PlacePlant":
      if not self.itemAt(pos):
        p = Plant(self.plantFactory)
        self.undoStack.push(CmdAddObject(self.garden, p, pos.x(), pos.y()))
    elif self.tool == "PlantRow":
      if not self.itemAt(pos):
        p = PlantRow(self.plantFactory)
        self.undoStack.push(CmdAddObject(self.garden, p, pos.x(), pos.y()))
    elif self.tool == "PlantBed":
      if not self.itemAt(pos):
        p = PlantBed(self.plantFactory)
        self.undoStack.push(CmdAddObject(self.garden, p, pos.x(), pos.y()))
    elif self.tool == "Ruler":
      if not self.itemAt(pos):
        p = RulerObject()
        self.undoStack.push(CmdAddObject(self.garden, p, pos.x(), pos.y()))

  def mouseReleaseEvent(self, event):
    QGraphicsScene.mouseReleaseEvent(self, event)
    if event.button() != Qt.LeftButton:
      return
    if len(self.selectedItems()) > 0 and event.scenePos() != self.oldPos:
      movedObjects = []
      for item in self.selectedItems():
        movedObjects.append(item.gardenObject)
      deltaPos = event.scenePos() - self.oldPos
      self.undoStack.push(CmdMoveObjects(self.garden, movedObjects, deltaPos.x(), deltaPos.y()))

  def drawBackground(self, painter, rect):
    # Disable grid when printing
    #if hasattr(painter, "printing"):
      #return

    gridSize = 50

    # Draw background image under grid
    QGraphicsScene.drawBackground(self, painter, rect)

    #drawImage ( const QRectF & target, const QImage & image, const QRectF & source, Qt::ImageConversionFlags flags = Qt::AutoColor )
    #print rect.x(), rect.y()
    #f = 1.
    
    #def printRect(r, name = "Rect"):
      #print name, r.left(), r.top(), r.right(), r.bottom()
      
    #printRect(rect, "rect")
    
    #sourceRect = QRectF(rect)
    
    #sourceRect.setCoords(rect.left()*f, rect.top()*f, rect.right()*f, rect.bottom()*f)
    #printRect(sourceRect, "sourceRect")
    #painter.drawImage(self.backgroundImage)
    
    
    painter.setPen(self.gridPen)
    left = int(rect.left()) - (int(rect.left()) % gridSize)
    top = int(rect.top()) - (int(rect.top()) % gridSize)
    lines = []
    for x in range (left, int(rect.right()), gridSize):
      lines.append(QLineF(x, rect.top(), x, rect.bottom()))
    for y in range (top, int(rect.bottom()), gridSize):
      lines.append(QLineF(rect.left(), y, rect.right(), y))

    painter.setRenderHint(painter.Antialiasing, False)
    painter.drawLines(lines)
    painter.setRenderHint(painter.Antialiasing, True)

class GardenView(QGraphicsView):
  def __init__(self, parent):
    QGraphicsView.__init__(self, parent)

    self.setScene(GardenScene(parent))
    #self.setSceneRect(-200, -200, 400, 400)
    self.setSceneRect(-sys.maxint/2, -sys.maxint/2, sys.maxint, sys.maxint)
    #self.setViewportUpdateMode(self.MinimalViewportUpdate)
    if ENABLE_OPENGL:
      self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)));
      self.setViewportUpdateMode(self.FullViewportUpdate)
    #self.setMinimumSize()

  def resizeEvent(self, resizeEvent):
    #print "Resize"
    QGraphicsView.resizeEvent(self, resizeEvent)
    #print self.sceneRect().width()
    #self.setSceneRect(QRectF(self.rect()))

  def mousePressEvent(self, event):
    if not event.buttons() & Qt.MidButton:
      return QGraphicsView.mousePressEvent(self, event)
    self.lastX = event.x()
    self.lastY = event.y()

  def mouseMoveEvent(self, event):
    if not event.buttons() & Qt.MidButton:
      return QGraphicsView.mouseMoveEvent(self, event)
    
    factor = 1 / self.matrix().mapRect(QRectF(0, 0, 1, 1)).width()
    dx = float(event.x() - self.lastX) * factor
    dy = float(event.y() - self.lastY) * factor
    
    self.lastX = event.x()
    self.lastY = event.y()
    self.setTransformationAnchor(self.NoAnchor)

    vsr = self.sceneRect()
    self.scene().setSceneRect(QRectF())
    sr = self.scene().sceneRect()

    #print "vr", vsr.left(), vsr.right()
    #print "sr", sr.left(), sr.right()
    #print "dx", dx, "dy", dy

    #if 1:
    #print vsr.left(), "-", dx, "<", sr.left(), "=", vsr.left() - dx < sr.left()
    #print vsr.right(), "-", dx, ">", sr.right(), "=", vsr.right() -dx > sr.right()

    
    #vsr.adjust(-dx, -dy, -dx, -dy)
    #self.setSceneRect(vsr)

    if vsr.left() > sr.left() and vsr.right() < sr.right():
      vsr.setLeft(vsr.left() - dx)
      vsr.setRight(vsr.left() - dx)
    if vsr.top() > sr.top() and vsr.bottom() < sr.bottom():
      vsr.setTop(vsr.top() - dy)
      vsr.setBottom(vsr.bottom() - dy)

    if dx < 0:
      if vsr.left() < sr.left():
        vsr.setLeft(vsr.left() - dx)
      elif vsr.right() - dx > sr.right():
        vsr.setRight(vsr.right() - dx)
      if vsr.top() < sr.top():
        vsr.setTop(vsr.top() - dy)
      elif vsr.bottom() - dy > sr.bottom():
        vsr.setBottom(vsr.bottom() - dy)
    else:
      if vsr.right() > sr.right():
        vsr.setRight(vsr.right() - dx)
        vsr.setLeft(vsr.left())
      elif vsr.left() - dx < sr.left():
        vsr.setLeft(vsr.left() - dx)
      if vsr.bottom() > sr.bottom():
        vsr.setBottom(vsr.bottom() - dy)
        vsr.setTop(vsr.top())
      elif vsr.top() - dy < sr.top():
        vsr.setTop(vsr.top() - dy)


    #self.setSceneRect(vsr)
    self.translate(dx, dy)
      
    #if vsr.right() - dx > sr.right():
      #print "setright"
      #vsr.setRight(vsr.right() - dx)
    #if vsr.top() - dy <= sr.top():
      #vsr.setTop(vsr.top() - dy)
    #if vsr.bottom() - dy >= sr.bottom():
      #vsr.setBottom(vsr.bottom() - dy)

    #if vsr.right() <= vsr.left():
      #vsr.setLeft(vsr.right() - dx)
    #if vsr.bottom() <= vsr.top():
      #vsr.setTop(vsr.bottom() - dy)

  def mouseReleaseEvent(self, event):
    if not event.buttons() & Qt.MidButton:
      return QGraphicsView.mouseReleaseEvent(self, event)

  def wheelEvent(self, event):
    self.setTransformationAnchor(self.AnchorUnderMouse)
    self.scaleView(math.pow(2.0, event.delta() / 240.0))

  def scaleView(self, scaleFactor):
    factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

    if factor < 0.04 or factor > 1000:
      return

    self.scale(scaleFactor, scaleFactor)
