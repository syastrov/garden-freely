from PyQt4.QtGui import *

class CmdAddObject(QUndoCommand):
  def __init__(self, garden, object, x, y):
    QUndoCommand.__init__(self, "Add %s" % object.getName())
    self.garden = garden
    self.object = object
    self.x = x
    self.y = y

  def redo(self):
    self.garden.addObject(self.object, self.x, self.y)

  def undo(self):
    self.garden.removeObject(self.object)

def multiDescription(verb, subject, count):
  """Return a description for a command operating on multiple objects"""
  plural = ""
  if count > 1:
    plural = "s"
  return "%s %d %s%s" % (verb, count, subject, plural)

class CmdMoveObjects(QUndoCommand):
  def __init__(self, garden, objects, dx, dy):
    QUndoCommand.__init__(self, multiDescription("Move", "Object", len(objects)))
    self.garden = garden
    self.objects = objects
    self.dx = dx
    self.dy = dy

  def redo(self):
    for p in self.objects:
      p.setPos(p.x + self.dx, p.y + self.dy)

  def undo(self):
    for p in self.objects:
      p.setPos(p.x - self.dx, p.y - self.dy)

class CmdRemoveObjects(QUndoCommand):
  def __init__(self, garden, objects):
    QUndoCommand.__init__(self, multiDescription("Remove", "Object", len(objects)))
    self.garden = garden
    self.objects = objects

  def redo(self):
    for p in self.objects:
      self.garden.removeObject(p)

  def undo(self):
    for p in self.objects:
      self.garden.addObject(p, p.x, p.y)



class CmdMoveGrip(QUndoCommand):
  def __init__(self, object, gripIndex, dx, dy):
    QUndoCommand.__init__(self, "Move Grip")
    self.object = object
    self.gripIndex = gripIndex
    self.dx = dx
    self.dy = dy
    self.first = True

  def redo(self):
    if self.first:
      self.first = False
      return
    grip = self.object.getGripAt(self.gripIndex)
    self.object.setGripPos(self.gripIndex, grip.x + self.dx, grip.y + self.dy)

  def undo(self):
    grip = self.object.getGripAt(self.gripIndex)
    self.object.setGripPos(self.gripIndex, grip.x - self.dx, grip.y - self.dy)