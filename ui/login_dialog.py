import os, requests, pathlib, requests, json

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.core import Qgis, QgsMessageLog

from .export_dialog import *
from ..ekmap_server.ekmap_common import *
from ..ekmap_server.ekmap_connector import eKConnector

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
        # Get login information
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()

        # Validate empty input
        if username == '' or password == '':
            QtWidgets.QMessageBox.about(self, 'Message', 'Username and password are required!')
            return

        # Login
        if eKConnector.login(username, password): # success
            self.txtUsername.setText('')
            self.txtPassword.setText('')
            self.parent.loginEvent()
            self.closeDialog()
        else: # fail
            QtWidgets.QMessageBox.about(self, "Message", "Login fail!")

    def closeDialog(self):
        self.close()