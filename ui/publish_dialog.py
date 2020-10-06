import os, requests, pathlib, requests, json

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.core import QgsProject

from .export_dialog import *
from ..ekmap_server.ekmap_common import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'publish_dialog.ui'))

class PublishDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent):
        """Constructor."""
        super(PublishDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.btnCancel.clicked.connect(self.closeDialog)
        self.btnOK.clicked.connect(self.publish)
        self.txtMapName.setText(QgsProject.instance().baseName())

    def publish(self):
        mapName = self.txtMapName.text().strip()
        if mapName == '':
            QtWidgets.QMessageBox.about(self, 'Message', 'Map name is required!')
        else:
            self.parent.mapName = mapName
            self.parent.publishEvent()

    def closeDialog(self):
        self.close()