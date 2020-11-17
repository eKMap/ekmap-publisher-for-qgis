import os, json, shutil, subprocess, signal, hashlib

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QSettings
from qgis.core import Qgis, QgsProject, QgsMessageLog

from .login_dialog import LoginDialog
from .export_dialog import ExportMapDialog
from .publish_dialog import PublishDialog
from ..ekmap_server.ekmap_common import *
from ..ekmap_server.ekmap_exporter import eKMapExporter
from ..ekmap_server.sprite_generator import SpriteGenerator

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
        inputServer = self.txtServer.text().strip()
        if currentServer != inputServer:
            if eKMapCommonHelper.isConnectionAvailable(inputServer):
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

        # Tạo thư mục xuất
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.progressBar.setValue(10)

        # Xuất thông tin MapInfo
        exporter = eKMapExporter(self.iface, QgsProject.instance())
        with open(filename, 'w') as outputFile:
            exportResult = exporter.exportMapInfo()
            exportResult["Title"] = self.mapName
            outputFile.write(json.dumps(exportResult, ensure_ascii = False))
        self.progressBar.setValue(30)

        # Lấy data source
        os.makedirs(TEMP_LOCATION, exist_ok=True)
        directoryOutput = os.path.dirname(filename)
        for layerCode, layerSource in exporter.sourcePaths.items():
            dirSource = os.path.dirname(layerSource)
            sourceBaseName = os.path.basename(layerSource).split(".")[0]
            filePaths = self._getFilesPathInDirWithSameName(dirSource, sourceBaseName)
            for filePath in filePaths:
                basename = os.path.basename(filePath)
                baseWithoutExtension = basename.split(".")[0]
                destPath = directoryOutput + "/" + 'source' + "/" + basename
                os.makedirs(os.path.dirname(destPath), exist_ok = True)
                shutil.copyfile(filePath, destPath)
        self.progressBar.setValue(40)

        # Lấy external graphic
        dstExternalGraphic = directoryOutput + "/sprite"
        os.makedirs(dstExternalGraphic, exist_ok = True)
        for externalGraphic in exporter.externalGraphics:
            shutil.copy2(externalGraphic, dstExternalGraphic)
        SpriteGenerator.generate(dstExternalGraphic)
        self.progressBar.setValue(50)

        # Nén package
        shutil.make_archive(self.exportDst + "/MapPackage", "zip", directoryOutput)
        self.progressBar.setValue(99)
            
        # Xóa file thừa
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

        self.progressBar.setValue(50)
        server = self.setting.value(SETTING_SERVER, "")
        authorization = 'Bearer ' + self.setting.value(SETTING_TOKEN)
        headers = {'Authorization': authorization}

        key = self.getKeyMapping()
        mappingDict = self.setting.value(SETTING_MAPPING, {})
        if mappingDict is None:
            mappingDict = {}
            
        # Upload
        self.lbMessage.setText('In process: Upload map')
        uploadFile = json.loads(self._upload(server, headers).text)
        if isUpdated:
            uploadFile['ItemId'] = int(mappingDict[key])
        self.progressBar.setValue(80)

        # Publish
        self.lbMessage.setText('In process: Publish map')
        result = self._publish(server, headers, uploadFile)
        self.progressBar.setValue(100)
        if result.text.isdigit():
            QtWidgets.QMessageBox.about(self, 'Message', 'Publish item successfully! \n' + self.mapName + ' (Id = ' + result.text + ')')
            # Store mapping
            mappingDict[key] = result.text
            self.setting.setValue(SETTING_MAPPING, mappingDict)
        else:
            QtWidgets.QMessageBox.about(self, 'Message', 'Publish item fail! ' + result.text)

    def _upload(self, server, headers):
        url = server + API_UPLOAD
        with open(self.exportDst + '/MapPackage.zip','rb') as file:
            files = {'mapPackage': file}
            return requests.post(url, headers = headers, files = files)

    def _publish(self, server, headers, data):
        url = server + API_PUBLISH
        headers["Content-Type"] = "application/json"
        return requests.put(url, headers = headers, json = data)

    def _isProjectContainsMapLayers(self):
        if len(QgsProject.instance().mapLayers()) == 0:
            QtWidgets.QMessageBox.about(self, 'Message', 'Project must have at least a map layer!')
            return False
        else:
            return True