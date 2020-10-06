import os

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.core import QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'export_dialog.ui'))

class ExportMapDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(ExportMapDialog, self).__init__(parent)
        self.setupUi(self)
        self.btnClose.clicked.connect(self.close)
        self.btnSelectExportPath.clicked.connect(self.selectOutputFolder)
        self.btnExport.clicked.connect(self.exportEvent)
        self.parent = parent
        self.txtMapName.setText(QgsProject.instance().baseName())

    def selectOutputFolder(self):
        filename = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.txtExportDestination.setText(filename)

    def exportEvent(self):
        mapName = self.txtMapName.text().strip()
        if mapName == '':
            QtWidgets.QMessageBox.about(self, 'Message', 'Map name is required!')
            return

        exportDst = self.txtExportDestination.text()
        # Lấy địa chỉ đường dẫn xuất và kiểm tra
        if not os.path.exists(exportDst):
            QMessageBox.about(self, "Error", "Invalid path")
            return
        self.txtMapName.setText(mapName)
        self.parent.exportDst = exportDst
        self.parent.mapName = mapName
        self.parent.exportEvent()