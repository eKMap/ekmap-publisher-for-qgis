import requests, json
from .ekmap_common import *
from .ekmap_logger import eKLogger
from qgis.PyQt.QtCore import QSettings

class eKConnector():

    # Whether that the connection to Server is OK
    def isConnectionAvailable(url):
        try:
            request = requests.get(url, timeout = 5, verify = False)
            return True
        except:
            return False

    # Whether the response is success or not
    def isResponseSuccess(resultText):
        result = json.loads(resultText)
        try:
            isSuccess = bool(result['success'])
            return isSuccess
        except:
            return False

    # Call LoginService
    def login(username, password):
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_LOGIN + '?userNameOrEmailAddress=' + username + '&password=' + password
        try:
            r = requests.post(url, verify = False)
            if eKConnector.isResponseSuccess(r.text):
                QSettings().setValue(SETTING_COOKIES, r.cookies)
                QSettings().setValue(SETTING_USERNAME, username)
                return True
            else:
                return False

        except Exception as ex:
            eKLogger.log(str(ex))
            return False

    # Call UploadService
    def upload(exportDst):
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_UPLOAD
        try:
            with open(exportDst + '/MapPackage.zip','rb') as file:
                files = {'mapPackage': file}
                cookies = QSettings().value(SETTING_COOKIES, None)
                r = requests.post(url, files = files, cookies = cookies, verify = False)
                return r
        except Exception as ex:
            eKLogger.log(str(ex))
            return None

    # Call PublishService
    def publish(data):
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_PUBLISH
        headers = {'Content-Type': 'application/json'}
        try:
            cookies = QSettings().value(SETTING_COOKIES, None)
            r = requests.post(url, headers = headers, cookies = cookies, json = data, verify = False)
            return r
        except Exception as ex:
            eKLogger.log(str(ex))
            return None