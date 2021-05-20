import os, json, shutil, subprocess, hashlib

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QSettings
from qgis.core import Qgis, QgsProject, QgsMessageLog

from .login_dialog import LoginDialog
from .export_dialog import ExportMapDialog
from .publish_dialog import PublishDialog
from ..ekmap_server.ekmap_common import *
from ..ekmap_server.ekmap_connector import eKConnector
from ..ekmap_server.ekmap_exporter import eKMapExporter
from ..ekmap_server.ekmap_logger import eKLogger

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ekmap_server_publisher_dockwidget_base.ui'))

class EKMapServerPublisherDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(EKMapServerPublisherDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.setting = QSettings()
        server = self.setting.value(SETTING_SERVER, "")
        if server != "":
            self.btnLogin.setEnabled(True)
            self.txtServer.setText(server)
        else:
            server = "https://server.ekgis.vn/"

        self.btnLogin.clicked.connect(self.openLoginDialog)
        self.btnLogout.clicked.connect(self.logoutEvent)
        self.btnSaveConfig.clicked.connect(self.saveConfig)
        self.btnExportMap.clicked.connect(self.openExportMapDialog)
        self.btnPublishMap.clicked.connect(self.openPublishMapDialog)
        self.btnUpdateMap.clicked.connect(self.updateEvent)
        self.logoutEvent()

        self.dlgLogin = None
        self.dlgExport = None
        self.dlgPublish = None
        self.exportDst = None
        self.iface = iface

        self.mapName = QgsProject.instance().baseName()

        # Listen event change
        QgsProject.instance().projectSaved.connect(self.checkUpdate)
        QgsProject.instance().metadataChanged.connect(self.checkUpdate)
        QgsProject.instance().crsChanged.connect(self.checkUpdate)

    def openExportMapDialog(self):
        if not self._isProjectContainsMapLayers():
            return

        if self.dlgExport is None:
            self.dlgExport = ExportMapDialog(parent = self)
        self.dlgExport.show()

    def openPublishMapDialog(self):
        if not self._isProjectContainsMapLayers():
            return
        
        if self.dlgPublish is None:
            self.dlgPublish = PublishDialog(parent = self)
        self.dlgPublish.show()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def saveConfig(self):
        currentServer = self.setting.value(SETTING_SERVER, "")
        inputServer = self.txtServer.text().strip().rstrip('/')
        if currentServer != inputServer:
            if eKConnector.isConnectionAvailable(inputServer):
                self.setting.setValue(SETTING_SERVER, inputServer)
                self.btnLogin.setEnabled(True)
                self.logoutEvent()
                QtWidgets.QMessageBox.about(self, 'Message', 'Connect successfully to:\n' + inputServer)
            else:
                QtWidgets.QMessageBox.about(self, 'Message', 'Connection is not available!')
                self.txtServer.setText(currentServer)

    def openLoginDialog(self):
        if self.dlgLogin is None:
            self.dlgLogin = LoginDialog(parent = self)
        self.dlgLogin.show()

    def loginEvent(self):
        username = self.setting.value(SETTING_USERNAME, "")
        self.lblWelcome.setText("Login as " + username)
        self.lblWelcome.show()
        self.btnLogout.show()
        self.btnPublishMap.setEnabled(True)

        self.btnLogin.hide()

    def logoutEvent(self):
        self.lblWelcome.hide()
        self.btnLogout.hide()
        self.btnPublishMap.setEnabled(False)
        self.btnUpdateMap.setEnabled(False)

        self.btnLogin.show()
        self.setting.setValue(SETTING_TOKEN, "")
        self.setting.setValue(SETTING_USERNAME, "")

    def exportEvent(self):
        self.dlgExport.close()
        self.inProgressState()
        try:
            self.lbMessage.setText("In progress: Export map")
            self.taskExport(True)
            path = self.exportDst.replace("/","\\")
            with subprocess.Popen(r'explorer "'+ path + '"'):
                self.outProgressState()

        except Exception as e:
            QtWidgets.QMessageBox.about(self, "Message", "Export fail! " + str(e))
            QgsMessageLog.logMessage(str(e), 'eKMapPublisher', level=Qgis.Info)

        finally:
            self.outProgressState()

    def publishEvent(self):
        self.dlgPublish.close()
        self.exportDst = TEMP_LOCATION
        self.inProgressState()

        try:
            self.taskPublish(False)
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "Message", "Publish fail! " + str(e))

        finally:
            self.outProgressState()
            self.btnUpdateMap.setEnabled(False)

    def updateEvent(self):
        if not self._isProjectContainsMapLayers():
            return

        self.exportDst = TEMP_LOCATION
        self.inProgressState()

        try:
            self.taskPublish(True)
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "Message", "Update fail! " + str(e))

        finally:
            self.outProgressState()
            self.btnUpdateMap.setEnabled(False)

    def checkUpdate(self):
        key = self.getKeyMapping()
        mappingDict = self.setting.value(SETTING_MAPPING, {})
        if key in mappingDict:
            self.btnUpdateMap.setEnabled(True)

    def getKeyMapping(self):
        projectPath = QgsProject.instance().absoluteFilePath()
        key = self.setting.value(SETTING_USERNAME, '') + self.setting.value(SETTING_SERVER, '') + projectPath
        key = hashlib.md5(key.encode()).hexdigest()
        return str(key)

    def inProgressState(self):
        self.tabWidget.setVisible(False)
        self.progressWidget.setVisible(True)

    def outProgressState(self):
        self.tabWidget.setVisible(True)
        self.progressWidget.setVisible(False)

    def taskExport(self, isClear):
        filename = self.exportDst + "/MapPackage/mapinfo.json"
        self.progressBar.setValue(0)

        try:
            # Create exported folder
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.progressBar.setValue(10)

            # Export MapInfo
            exporter = eKMapExporter(self.iface, QgsProject.instance())
            with open(filename, 'w') as outputFile:
                exportResult = exporter.exportMapInfo()
                exportResult["Title"] = self.mapName
                outputFile.write(json.dumps(exportResult, ensure_ascii = False))
            self.progressBar.setValue(30)

            # Get data source
            directoryOutput = os.path.dirname(filename)
            dstPath = directoryOutput + "/" + 'source'
            os.makedirs(dstPath, exist_ok=True)
            for layerCode, layerSource in exporter.sourcePaths.items():
                eKLogger.log(layerCode + ' ^^^ ' + layerSource)
                if os.path.isdir(layerSource):
                    foldername = os.path.basename(layerSource)
                    dstFolder = dstPath + '/' + foldername
                    if not os.path.exists(dstFolder):
                        shutil.copytree(layerSource, dstFolder)
                else:
                    shutil.copy2(layerSource, dstPath)
            self.progressBar.setValue(40)

            # Get external graphic
            dstExternalGraphic = directoryOutput + "/sprite"
            
            os.makedirs(dstExternalGraphic, exist_ok = True)
            for externalGraphic in exporter.externalGraphics:
                shutil.copy2(externalGraphic, dstExternalGraphic)
            # SpriteGenerator.generate(dstExternalGraphic)
            self.progressBar.setValue(50)

            # Compress package
            shutil.make_archive(self.exportDst + "/MapPackage", "zip", directoryOutput)
            self.progressBar.setValue(99)

        finally:
            # Delete temp file
            if isClear: # Trường hợp Publish thì sẽ chưa xóa vội mà để xử lý cuối cùng mới thực hiện
                eKMapCommonHelper.cleanTempDir()
            shutil.rmtree(self.exportDst + "/MapPackage")
            self.progressBar.setValue(100)

    # Lấy tất cả các file trong thư mục có cùng tên
    def _getFilesPathInDirWithSameName(self, directory, name):
        filePaths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                if filename.split(".")[0] == name:
                    filePath = os.path.join(root, filename)
                    filePaths.append(filePath)
        return filePaths

    def taskPublish(self, isUpdated):
        # Export zip file
        self.lbMessage.setText('In process: Wrap map data')
        self.taskExport(False)

        try:
            self.progressBar.setValue(50)

            key = self.getKeyMapping()
            mappingDict = self.setting.value(SETTING_MAPPING, {})
            if mappingDict is None:
                mappingDict = {}
                
            # Upload
            self.lbMessage.setText('In process: Upload map')
            uploadResult = eKConnector.upload(self.exportDst)
            packageInfo = json.loads(uploadResult.text)['result']
            infoResult = eKConnector.info(packageInfo)
            uploadFile = json.loads(infoResult.text)['result']
            uploadFile['packageInfo'] = packageInfo
            eKLogger.log(uploadFile)
            if isUpdated:
                uploadFile['MapId'] = int(mappingDict[key])
            self.progressBar.setValue(80)

            # Publish
            self.lbMessage.setText('In process: Publish map')
            r = eKConnector.publish(uploadFile)
            result = json.loads(r.text)
            self.progressBar.setValue(100)
            if result['success']:
                mapId = result['result']
                QtWidgets.QMessageBox.about(self, 'Message', 'Publish map successfully! \n' + self.mapName + ' (Id = ' + mapId + ')')
                # Store mapping
                mappingDict[key] = mapId
                self.setting.setValue(SETTING_MAPPING, mappingDict)
            else:
                QtWidgets.QMessageBox.about(self, 'Message', 'Publish map fail! ' + r.text)
        
        finally:
            eKMapCommonHelper.cleanTempDir()

    def _isProjectContainsMapLayers(self):
        if len(QgsProject.instance().mapLayers()) == 0:
            QtWidgets.QMessageBox.about(self, 'Message', 'Project must have at least a map layer!')
            return False
        else:
            return True