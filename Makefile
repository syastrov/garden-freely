generate:
	pyuic4 -o ui_gardenproperties.py gardenproperties.ui
	pyuic4 -o ui_mainwindow.py mainwindow.ui
	pyrcc4 -o gardenfreely_rc.py gardenfreely.qrc
