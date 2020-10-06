import os, requests, pathlib, requests, json

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import QSettings
from qgis.core import Qgis, QgsMessageLog

from .export_dialog import *
from ..ekmap_server.ekmap_common import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'login_dialog.ui'))

class LoginDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent):
        """Constructor."""
        super(LoginDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.btnCancel.clicked.connect(self.closeDialog)
        self.btnOK.clicked.connect(self.login)

    def login(self):
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()
        if username == '' or password == '':
            QtWidgets.QMessageBox.about(self, 'Message', 'Username and password are required!')
            return

        # Lấy thông tin cấu hình server
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_LOGIN
        try:
            r = requests.post(url, json = {
                "userNameOrEmailAddress": username,
                "password": password,
            })
            result = json.loads(r.text)
        
            QSettings().setValue(SETTING_TOKEN, result['result']['accessToken'])
            QSettings().setValue(SETTING_USERNAME, username)
            self.txtUsername.setText('')
            self.txtPassword.setText('')
            self.parent.loginEvent()
            self.closeDialog()
        except: 
            QtWidgets.QMessageBox.about(self, "Message", "Login fail!")

    def closeDialog(self):
        self.close()