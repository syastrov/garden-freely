from PyQt4.QtCore import *
from PyQt4.Qt import *

from xml.dom import minidom

from gardengraphicsitem import *

def getAttr(node, attribute, default=None):
  if node.hasAttribute(attribute):
    return node.getAttribute(attribute)
  else:
    return default

class GardenFileException:
  def __init__(self, reason):
    self.reason = reason

class PlantDBFileException:
  def __init__(self, reason):
    self.reason = reason

class AbstractMethodException:
  def __init__(self, reason):
    self.reason = reason

class Garden(QObject):
  def __init__(self, parent = None):
    QObject.__init__(self, parent)
    self.objects = []
    self.backgroundImage = ""
    self.backgroundImageScale = 1.0
    self.backgroundOpacity = 1.0

  def load(self, fileName):
    self.clear()
    xml = minidom.parse(fileName)
    if not xml.firstChild or xml.firstChild.tagName != "garden":
      raise GardenFileException("Not a valid garden file: No <garden> root tag.")

    garden = xml.firstChild
    self.setBackgroundImage(getAttr(garden, "backgroundImage", ""))
    self.setBackgroundImageScale(float(getAttr(garden, "backgroundImageScale", 1.0)))
    self.setBackgroundOpacity(float(getAttr(garden, "backgroundOpacity", 1.0)))

    for e in xml.getElementsByTagName("ruler"):
      p = RulerObject()
      p.read(e)
      self.objects.append(p)
    for e in xml.getElementsByTagName("plantBed"):
      species = e.getAttribute("species")
      factory = PlantDB[species]
      if not factory:
        raise GardenFileException("plantBed: No such species %s" % species)
      p = PlantBed(factory)
      p.read(e)
      self.objects.append(p)
    for e in xml.getElementsByTagName("plantRow"):
      species = e.getAttribute("species")
      factory = PlantDB[species]
      if not factory:
        raise GardenFileException("plantRow: No such species %s" % species)
      p = PlantRow(factory)
      p.read(e)
      self.objects.append(p)
    for e in xml.getElementsByTagName("plant"):
      species = e.getAttribute("species")
      factory = PlantDB[species]
      if not factory:
        raise GardenFileException("plant: No such species %s" % species)
      p = Plant(factory)
      p.read(e)
      self.objects.append(p)
      
    self.emit(SIGNAL("loaded"))
    return True

  def save(self, fileName):
    xml = minidom.Document()
    garden = xml.createElement("garden")
    xml.appendChild(garden)
    garden.setAttribute("backgroundImage", self.backgroundImage)
    garden.setAttribute("backgroundImageScale", str(self.backgroundImageScale))
    garden.setAttribute("backgroundOpacity", str(self.backgroundOpacity))
    for p in self.objects:
      n = xml.createElement(p.tagName)
      garden.appendChild(n)
      p.write(n)

    f = open(fileName, "w")
    self.emit(SIGNAL("saved"))
    return xml.writexml(f, "  ", "", "\n")

  def clear(self):
    del self.objects[:]
    self.setBackgroundImage("")
    self.setBackgroundImageScale(1.0)
    self.setBackgroundOpacity(1.0)
    self.emit(SIGNAL("cleared"))

  def addObject(self, object, x, y):
    object.garden = self
    object.x = x
    object.y = y
    self.objects.append(object)
    self.emit(SIGNAL("objectAdded"), object)

  def removeObject(self, object):
    self.emit(SIGNAL("objectRemoved"), object)
    return self.objects.remove(object)

  def setBackgroundImage(self, backgroundImage):
    if backgroundImage != self.backgroundImage:
      self.backgroundImage = backgroundImage
      self.emit(SIGNAL("backgroundImageSet"), backgroundImage)

  def setBackgroundImageScale(self, backgroundImageScale):
    if backgroundImageScale != self.backgroundImageScale:
      self.backgroundImageScale = backgroundImageScale
      self.emit(SIGNAL("backgroundImageScaleSet"), backgroundImageScale)

  def setBackgroundOpacity(self, backgroundOpacity):
    if backgroundOpacity != self.backgroundOpacity:
      self.backgroundOpacity = backgroundOpacity
      self.emit(SIGNAL("backgroundOpacitySet"), backgroundOpacity)

class GardenObject(QObject):
  def __init__(self, tagName, parent = None):
    QObject.__init__(self, parent)
    self.tagName = tagName

  def read(self, n):
    self.x = float(getAttr(n, "x"))
    self.y = float(getAttr(n, "y"))

  def write(self, n):
    n.setAttribute("x", str(self.x))
    n.setAttribute("y", str(self.y))

  def getName(self):
    return self.tagName.capitalize()

  def setPos(self, x, y,):
    self.x = x
    self.y = y
    self.emit(SIGNAL("posChanged"), x, y)


class Plant(GardenObject):
  def __init__(self, factory):
    GardenObject.__init__(self, "plant", factory)
    self.factory = factory

  def getName(self):
    return "Plant (%s)" % self.factory.species

  def species(self):
    return self.factory.species

  def createGraphicsItem(self):
    return PlantGraphicsItem(self)

  def read(self, n):
    GardenObject.read(self, n)

  def write(self, n):
    GardenObject.write(self, n)
    n.setAttribute("species", self.factory.species)

class Grip:
  def __init__(self, index, x = 0, y = 0):
    self.index = index
    self.x = x
    self.y = y

class GrippableObject(GardenObject):
  def __init__(self, tagName, numGrips, parent = None):
    GardenObject.__init__(self, tagName)
    self.grips = []
    for i in range(numGrips):
      self.grips.append(Grip(i))

    self.sharedRenderer = None

  def getSharedRenderer(self):
    if not self.sharedRenderer:
      self.sharedRenderer = QSvgRenderer(self.getGripIcon())
    return self.sharedRenderer

  def getGripIcon(self):
    raise AbstractMethodException("getGripIcon")

  def read(self, n):
    GardenObject.read(self, n)
    for i in range(len(self.grips)):
      self.grips[i].x = float(getAttr(n, "x%d" % (i+1), 0))
      self.grips[i].y = float(getAttr(n, "y%d" % (i+1), 0))
      
  def write(self, n):
    GardenObject.write(self, n)
    for i in range(len(self.grips)):
      n.setAttribute("x%d" % (i+1), str(self.grips[i].x))
      n.setAttribute("y%d" % (i+1), str(self.grips[i].y))

  def getGripAt(self, gripIndex):
    return self.grips[gripIndex]

  def setGripPos(self, gripIndex, x, y):
    self.grips[gripIndex].x = x
    self.grips[gripIndex].y = y
    self.emit(SIGNAL("gripPosChanged"), gripIndex, x, y)

class RulerObject(GrippableObject):
  def __init__(self):
    GrippableObject.__init__(self, "ruler", 2)
    self.grips[1].x = 50

  def createGraphicsItem(self):
    return RulerGraphicsItem(self)

  def getGripIcon(self):
    return "images/grip.svg"

  def read(self, n):
    GrippableObject.read(self, n)

  def write(self, n):
    GrippableObject.write(self, n)

class PlantRow(GrippableObject):
  def __init__(self, factory):
    GrippableObject.__init__(self, "plantRow", 2, factory)
    self.factory = factory
    self.grips[1].x = 50

  def createGraphicsItem(self):
    return PlantRowGraphicsItem(self)

  def getGripIcon(self):
    return self.factory.icon

  def read(self, n):
    GrippableObject.read(self, n)

  def write(self, n):
    GrippableObject.write(self, n)
    n.setAttribute("species", self.factory.species)

class PlantBed(GrippableObject):
  def __init__(self, factory):
    GrippableObject.__init__(self, "plantBed", 2, factory)
    self.factory = factory
    self.grips[1].x = 50
    self.grips[1].y = 50

  def createGraphicsItem(self):
    return PlantBedGraphicsItem(self)

  def getGripIcon(self):
    return self.factory.icon

  def read(self, n):
    GrippableObject.read(self, n)

  def write(self, n):
    GrippableObject.write(self, n)
    n.setAttribute("species", self.factory.species)


class PlantFactory(QObject):
  def __init__(self, species, parent = None):
    QObject.__init__(self, parent)
    self.species = species
    self.plantSpacing = 0
    self.rowSpacing = 0
    self.sharedRenderer = None

  def getSharedRenderer(self):
    if not self.sharedRenderer:
      self.sharedRenderer = QSvgRenderer(self.icon)
    return self.sharedRenderer
  
  def read(self, n):
    self.icon = "plants/" + getAttr(n, "icon", "default.svg")
    self.plantSpacing = float(getAttr(n, "plantSpacing", 0))
    self.rowSpacing = float(getAttr(n, "rowSpacing", 0))

  def create(self):
    return Plant(self)

  def __str__(self):
    return "<PlantFactory species=%s icon=%s>" % (self.species, self.icon)

class PlantDatabase:
  def __init__(self):
    self.plants = {}
    xml = minidom.parse("plants/plants.xml")
    for e in xml.getElementsByTagName("plant"):
      if not e.hasAttribute("species"):
        raise PlantDBFileException("Plant factory has no species attribute")
      name = e.getAttribute("species")
      p = PlantFactory(name)
      self.plants[name] = p
      p.read(e)
      
  def plantFactoryAt(self, idx):
    return self.plants[self.plants.keys()[idx]]
  
  def __getitem__(self, item):
    if self.plants.has_key(item):
      return self.plants[item]
    else:
      return None

  def __iter__(self):
    return iter(self.plants)
  
  def __len__(self):
    return len(self.plants)

PlantDB = PlantDatabase()