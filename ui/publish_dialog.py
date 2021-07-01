import os

from qgis.PyQt import QtWidgets, uic
from qgis.core import QgsProject

from .export_dialog import *
from ..ekmap_server.ekmap_common import *
from ..ekmap_server.ekmap_connector import eKConnector

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

        self.collections = [{'title': 'Site (root)', 'id': 0}]
        self.collections.extend(eKConnector.getCollection())
        for collection in self.collections:
            self.cbCollection.addItem(collection['title'])

    def publish(self):
        currentIndex = self.cbCollection.currentIndex()
        collectionId = self.collections[currentIndex]['id']
        mapName = self.txtMapName.text().strip()
        if mapName == '':
            QtWidgets.QMessageBox.about(self, 'Message', 'Map name is required!')
        else:
            self.parent.mapName = mapName
            self.parent.publishEvent(collectionId)

    def closeDialog(self):
        self.close()