from PyQt4.Qt import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *

from math import pi, atan2

from commands import *

sceneUnitsPerFt = 50.0

selectionRectPen = QPen(Qt.blue, 1, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin)
selectionRectPen.setCosmetic(True)

plantSpacingPen = QPen(QColor(0, 168, 0, 128))
plantSpacingBrush = QBrush(QColor(0, 168, 0, 64))

def sizeToPoint(size):
  return QPointF(size.width(), size.height())

class GripGraphicsItem(QGraphicsSvgItem):
  def __init__(self, grippableObject, gripIndex):
    QGraphicsSvgItem.__init__(self)
    self.grippableObject = grippableObject
    
    self.gripIndex = gripIndex
    self.grip = self.grippableObject.getGripAt(gripIndex)
    
    self.setSharedRenderer(grippableObject.getSharedRenderer())
    
    #self.setFlags(self.ItemIgnoresTransformations)

    s = self.renderer().defaultSize()
    w = s.width()
    h = s.height()
    self.setTransform(QTransform().translate(-w/2,-h/2))

    self.updatePos()

  def mousePressEvent(self, event):
    self.mousePos = event.pos()
    self.gripX = self.grip.x
    self.gripY = self.grip.y

  def mouseMoveEvent(self, event):
    pos = event.pos()
    gripPos = QPointF(self.grip.x, self.grip.y) + (pos - self.mousePos)
    self.grippableObject.setGripPos(self.gripIndex, gripPos.x(), gripPos.y())

  def mouseReleaseEvent(self, event):
    self.scene().undoStack.push(CmdMoveGrip(self.grippableObject, self.gripIndex, self.grip.x - self.gripX, self.grip.y - self.gripY))

  def updatePos(self):
    self.setPos(self.grip.x, self.grip.y)

class PlantRowGraphicsItem(QGraphicsLineItem):
  normalPen = QPen(Qt.black, 5, Qt.SolidLine, Qt.FlatCap)
  selectedPen = QPen(Qt.blue, 5, Qt.SolidLine, Qt.FlatCap)
  def __init__(self, row):
    QGraphicsLineItem.__init__(self)
    self.gardenObject = row

    self.normalPen.setCosmetic(True)
    self.selectedPen.setCosmetic(True)

    self.headGrip = GripGraphicsItem(row, 0)
    self.tailGrip = GripGraphicsItem(row, 1)
    self.headGrip.setParentItem(self)
    self.tailGrip.setParentItem(self)

    self.setPos(row.x, row.y)
    grip0 = row.getGripAt(0)
    grip1 = row.getGripAt(1)
    self.setLine(grip0.x, grip0.y, grip1.x, grip1.y)

    self.setPen(self.normalPen)
    
    self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
    QObject.connect(row, SIGNAL("posChanged"), self.setPos)
    QObject.connect(row, SIGNAL("gripPosChanged"), self.gripPosChanged)

  def gripPosChanged(self, gripIndex, x, y):
    grip = self.gardenObject.getGripAt(gripIndex)
    line = self.line()
    if gripIndex == 0:
      newLine = QLineF(QPointF(grip.x, grip.y), line.p2())
    else:
      newLine = QLineF(line.p1(), QPointF(grip.x, grip.y))
    self.setLine(newLine)
    self.headGrip.updatePos()
    self.tailGrip.updatePos()

  def itemChange(self, change, value):
    if change == self.ItemSelectedChange:
      isSelected = value.toBool()
      if isSelected:
        self.setPen(self.selectedPen)
      else:
        self.setPen(self.normalPen)
      return value
    return QGraphicsItem.itemChange(self, change, value)

  def paint(self, painter, options, widget):
    #if self.scene().showRowSpacing:
      #s = self.gardenObject.factory.rowSpacing
      #painter.setPen(plantSpacingPen)
      #painter.setBrush(plantSpacingBrush)
      #l = self.line()
      #painter.drawRect(l.x1(), l.y1() - s, l.x2(), l.y2() + s)
    QGraphicsLineItem.paint(self, painter, options, widget)


class RulerGraphicsItem(QGraphicsLineItem):
  normalPen = QPen(Qt.black, 2, Qt.DotLine, Qt.FlatCap)
  selectedPen = QPen(Qt.blue, 2, Qt.DotLine, Qt.FlatCap)
  def __init__(self, ruler):
    QGraphicsLineItem.__init__(self)
    self.gardenObject = ruler

    self.headGrip = GripGraphicsItem(ruler, 0)
    self.tailGrip = GripGraphicsItem(ruler, 1)
    self.headGrip.setParentItem(self)
    self.tailGrip.setParentItem(self)

    self.rulerText = QGraphicsTextItem(self)
    self.rulerText.setParentItem(self)

    self.setPos(ruler.x, ruler.y)
    grip0 = ruler.getGripAt(0)
    grip1 = ruler.getGripAt(1)
    self.setLine(grip0.x, grip0.y, grip1.x, grip1.y)
    self.updateRulerText()

    self.normalPen.setCosmetic(True)
    self.selectedPen.setCosmetic(True)
    self.setPen(self.normalPen)
    
    self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
    QObject.connect(ruler, SIGNAL("posChanged"), self.setPos)
    QObject.connect(ruler, SIGNAL("gripPosChanged"), self.gripPosChanged)

  def gripPosChanged(self, gripIndex, x, y):
    grip = self.gardenObject.getGripAt(gripIndex)
    line = self.line()
    if gripIndex == 0:
      newLine = QLineF(QPointF(grip.x, grip.y), line.p2())
    else:
      newLine = QLineF(line.p1(), QPointF(grip.x, grip.y))
    self.setLine(newLine)
    self.headGrip.updatePos()
    self.tailGrip.updatePos()
    self.updateRulerText()

    
  def updateRulerText(self):
    line = self.line()
    lengthInFt = line.length() / sceneUnitsPerFt
    self.rulerText.setPlainText("%.3f ft" % lengthInFt)

    # All this just to make the text always on top
    w = self.rulerText.document().size().width()
    h = self.rulerText.document().size().height()
    angle = atan2(line.dy(), line.dx())
    
    # If it's on the left side of the circle...
    if not (angle > -pi/2 and angle < pi/2):
      # Flip it, and change the offset to reflect the flipping
      angle += pi
      w = -w
      h = -h

    # Get middle point of line
    textPos = line.pointAt(0.5 - w / 2 / line.length())

    # Create a normal, so we can offset the text correctly
    normal = line.normalVector()
    
    # Move it to the middle of the line and set it's length to text height
    normal.translate(textPos - line.p1())
    normal.setLength(h)

    # Use the end point of the normal vector as text pos
    self.rulerText.setPos(normal.p2())
    self.rulerText.setTransform(QTransform().rotateRadians(angle))

  def itemChange(self, change, value):
    if change == self.ItemSelectedChange:
      isSelected = value.toBool()
      if isSelected:
        self.setPen(self.selectedPen)
      else:
        self.setPen(self.normalPen)
      return value
    return QGraphicsItem.itemChange(self, change, value)

class PlantBedGraphicsItem(QGraphicsRectItem):
  normalPen = QPen(Qt.black, 5, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)
  selectedPen = QPen(Qt.blue, 5, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)
  normalBrush = QBrush(QColor("#bea795"), Qt.BDiagPattern)
  def __init__(self, bed):
    QGraphicsRectItem.__init__(self)
    self.gardenObject = bed

    self.headGrip = GripGraphicsItem(bed, 0)
    self.tailGrip = GripGraphicsItem(bed, 1)
    self.headGrip.setParentItem(self)
    self.tailGrip.setParentItem(self)

    self.setPos(bed.x, bed.y)
    grip0 = bed.getGripAt(0)
    grip1 = bed.getGripAt(1)
    self.setRect(grip0.x, grip0.y, grip1.x - grip0.x, grip1.y - grip0.y)

    self.normalPen.setCosmetic(True)
    self.selectedPen.setCosmetic(True)

    self.setPen(self.normalPen)
    self.setBrush(self.normalBrush)
    
    self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
    QObject.connect(bed, SIGNAL("posChanged"), self.setPos)
    QObject.connect(bed, SIGNAL("gripPosChanged"), self.gripPosChanged)

  def gripPosChanged(self, gripIndex, x, y):
    grip = self.gardenObject.getGripAt(gripIndex)
    rect = self.rect()
    if gripIndex == 0:
      rect.setTopLeft(QPointF(grip.x, grip.y))
    else:
      rect.setBottomRight(QPointF(grip.x, grip.y))
    self.setRect(rect)
    self.headGrip.updatePos()
    self.tailGrip.updatePos()
    

  def itemChange(self, change, value):
    if change == self.ItemSelectedChange:
      isSelected = value.toBool()
      if isSelected:
        self.setPen(self.selectedPen)
      else:
        self.setPen(self.normalPen)
      return value
    return QGraphicsItem.itemChange(self, change, value)

#class PlantSpacingItem(QGraphicsEllipseItem):
  #def __init__(self, plant):
    #QGraphicsEllipseItem.__init__(self)
    #self.plant = plant
    #s = plant.factory.plantSpacing
    #self.setPen(QPen(QColor(0, 168, 0, 128)))
    #self.setBrush(QBrush(QColor(0, 168, 0, 64)))
    #self.setRect(-s, -s, s*2, s*2)

class PlantGraphicsItem(QGraphicsSvgItem):
  def __init__(self, plant):
    QGraphicsSvgItem.__init__(self)
    self.gardenObject = plant
    self.setSharedRenderer(plant.factory.getSharedRenderer())
    self.setPos(plant.x, plant.y)

    self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        
    #self.setFlags(self.ItemIgnoresTransformations)
    #self.plantSpacingItem = PlantSpacingItem(self.gardenObject)
    #self.plantSpacingItem.setParentItem(self)

    s = self.renderer().defaultSize()
    w = s.width()
    h = s.height()
    self.setTransform(QTransform().translate(-w/2,-h/2))

    self.connect(self.gardenObject, SIGNAL("posChanged"), self.setPos)

  def paint(self, painter, options, widget):
    if self.scene().showPlantSpacing:
      s = self.gardenObject.factory.plantSpacing
      ds = self.renderer().defaultSize()
      w = ds.width()
      h = ds.height()
      painter.save()
      painter.translate(w/2,h/2)
      painter.setPen(plantSpacingPen)
      painter.setBrush(plantSpacingBrush)
      painter.drawEllipse(-s, -s, s*2, s*2)
      painter.restore()
    QGraphicsSvgItem.paint(self, painter, options, widget)
