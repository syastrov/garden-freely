# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gardenproperties.ui'
#
# Created: Thu Oct  3 20:54:24 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_GardenProperties(object):
    def setupUi(self, GardenProperties):
        GardenProperties.setObjectName(_fromUtf8("GardenProperties"))
        GardenProperties.resize(357, 259)
        self.vboxlayout = QtGui.QVBoxLayout(GardenProperties)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tabWidget = QtGui.QTabWidget(GardenProperties)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.vboxlayout1 = QtGui.QVBoxLayout(self.tab)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.hboxlayout.addWidget(self.label_3)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.backgroundImageEdit = QtGui.QLineEdit(self.tab)
        self.backgroundImageEdit.setText(_fromUtf8(""))
        self.backgroundImageEdit.setObjectName(_fromUtf8("backgroundImageEdit"))
        self.hboxlayout1.addWidget(self.backgroundImageEdit)
        self.browseBackgroundButton = QtGui.QPushButton(self.tab)
        self.browseBackgroundButton.setObjectName(_fromUtf8("browseBackgroundButton"))
        self.hboxlayout1.addWidget(self.browseBackgroundButton)
        self.hboxlayout.addLayout(self.hboxlayout1)
        self.vboxlayout1.addLayout(self.hboxlayout)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout2.addWidget(self.label)
        self.scaleSpinBox = QtGui.QDoubleSpinBox(self.tab)
        self.scaleSpinBox.setPrefix(_fromUtf8(""))
        self.scaleSpinBox.setSingleStep(0.1)
        self.scaleSpinBox.setProperty("value", 1.0)
        self.scaleSpinBox.setObjectName(_fromUtf8("scaleSpinBox"))
        self.hboxlayout2.addWidget(self.scaleSpinBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout2)
        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setObjectName(_fromUtf8("hboxlayout3"))
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout3.addWidget(self.label_2)
        self.opacitySlider = QtGui.QSlider(self.tab)
        self.opacitySlider.setMaximum(255)
        self.opacitySlider.setSliderPosition(255)
        self.opacitySlider.setOrientation(QtCore.Qt.Horizontal)
        self.opacitySlider.setInvertedAppearance(False)
        self.opacitySlider.setInvertedControls(False)
        self.opacitySlider.setTickPosition(QtGui.QSlider.TicksAbove)
        self.opacitySlider.setObjectName(_fromUtf8("opacitySlider"))
        self.hboxlayout3.addWidget(self.opacitySlider)
        self.vboxlayout1.addLayout(self.hboxlayout3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.vboxlayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(GardenProperties)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.vboxlayout.addWidget(self.buttonBox)
        self.label_3.setBuddy(self.backgroundImageEdit)
        self.label.setBuddy(self.scaleSpinBox)
        self.label_2.setBuddy(self.opacitySlider)

        self.retranslateUi(GardenProperties)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GardenProperties)
        GardenProperties.setTabOrder(self.backgroundImageEdit, self.browseBackgroundButton)
        GardenProperties.setTabOrder(self.browseBackgroundButton, self.scaleSpinBox)
        GardenProperties.setTabOrder(self.scaleSpinBox, self.buttonBox)
        GardenProperties.setTabOrder(self.buttonBox, self.tabWidget)

    def retranslateUi(self, GardenProperties):
        GardenProperties.setWindowTitle(QtGui.QApplication.translate("GardenProperties", "Garden Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("GardenProperties", "&Image:", None, QtGui.QApplication.UnicodeUTF8))
        self.browseBackgroundButton.setText(QtGui.QApplication.translate("GardenProperties", "&Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GardenProperties", "&Scale:", None, QtGui.QApplication.UnicodeUTF8))
        self.scaleSpinBox.setSuffix(QtGui.QApplication.translate("GardenProperties", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GardenProperties", "&Opacity:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("GardenProperties", "&Background", None, QtGui.QApplication.UnicodeUTF8))

