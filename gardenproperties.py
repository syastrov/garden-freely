from ui_gardenproperties import Ui_GardenProperties

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class GardenPropertiesDialog(QDialog):
  def __init__(self, garden, parent = None):
    QDialog.__init__(self, parent)
    self.ui = Ui_GardenProperties()
    self.ui.setupUi(self)

    self.garden = garden

    self.connect(self.garden, SIGNAL("backgroundImageSet"), self.gardenBackgroundImageSet)
    self.connect(self.garden, SIGNAL("backgroundImageScaleSet"), self.gardenBackgroundImageScaleSet)
    self.connect(self.garden, SIGNAL("backgroundOpacitySet"), self.gardenBackgroundOpacitySet)

  def gardenBackgroundImageSet(self, backgroundImage):
    self.ui.backgroundImageEdit.setText(backgroundImage)

  def gardenBackgroundImageScaleSet(self, scale):
    self.ui.scaleSpinBox.setValue(scale)

  def gardenBackgroundOpacitySet(self, opacity):
    self.ui.opacitySlider.setValue(opacity*255.0)

  @pyqtSignature("")
  def on_browseBackgroundButton_clicked(self):
    formats = ' '.join(['*.%s' % str(f) for f in QImageReader.supportedImageFormats()])

    fileName = QFileDialog.getOpenFileName(self,
        self.tr("Choose Background Image"), "", self.tr("Image Files") + "(%s)" % formats)
    if fileName:
      self.ui.backgroundImageEdit.setText(fileName)

  def on_buttonBox_clicked(self, button):
    bbox = self.ui.buttonBox
    role = bbox.buttonRole(button)
    if role == bbox.ApplyRole:
      self.onApply()
    elif role == bbox.AcceptRole:
      self.onApply()
      self.hide()
    elif role == bbox.RejectRole:
      self.hide()

  def onApply(self):
    self.garden.setBackgroundImage(self.ui.backgroundImageEdit.text())
    self.garden.setBackgroundImageScale(self.ui.scaleSpinBox.value())
    self.garden.setBackgroundOpacity(self.ui.opacitySlider.value()/255.0)