import requests, json
from .ekmap_common import *
from .ekmap_logger import eKLogger
from qgis.PyQt.QtCore import QSettings

class eKConnector():

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
        url = server + API_LOGIN # Login using eKMap Server Account
        result = eKConnector.__login(username, password, url)
        if result is False:
            url = server + API_EXTERNAL_LOGIN # Login using eKMap Clound Account
            result = eKConnector.__login(username, password, url)
        return result

    def __login(username, password, url):
        try:
            r = requests.post(url, json= {
                "userNameOrEmailAddress": username,
                "password": password,
            } ,verify = False)
            if eKConnector.isResponseSuccess(r.text):
                eKLogger.log(r.text)
                result = json.loads(r.text)
                QSettings().setValue(SETTING_TOKEN, result['result']['accessToken'])
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
        authorization = 'Bearer ' + QSettings().value(SETTING_TOKEN, "")
        headers = {'Authorization': authorization}
        eKLogger.log(url)
        try:
            with open(exportDst + '/MapPackage.zip','rb') as file:
                files = {'mapPackage': file}
                # cookies = QSettings().value(SETTING_COOKIES, None)
                r = requests.post(url, files = files, headers = headers, verify = False)
                return r
        except Exception as ex:
            eKLogger.log(str(ex))
            return None

    def info(uploadedPackageInfo):
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_INFO
        authorization = 'Bearer ' + QSettings().value(SETTING_TOKEN, "")
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }
        try:
            r = requests.post(url, headers = headers, json = uploadedPackageInfo, verify = False)
            return r
        except Exception as ex:
            eKLogger.log(str(ex))
            return None

    # Call PublishService
    def publish(data):
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_PUBLISH
        authorization = 'Bearer ' + QSettings().value(SETTING_TOKEN, "")
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }
        try:
            # cookies = QSettings().value(SETTING_COOKIES, None)
            r = requests.post(url, headers = headers, json = data, verify = False)
            return r
        except Exception as ex:
            eKLogger.log(str(ex))
            return None

    def getCollection():
        server = QSettings().value(SETTING_SERVER, "")
        url = server + API_COLLECTION
        authorization = 'Bearer ' + QSettings().value(SETTING_TOKEN, "")
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }
        try:
            r = requests.get(url, headers = headers, verify = False)
            if eKConnector.isResponseSuccess(r.text):
                result = json.loads(r.text)
                return result['result']
            else:
                return ['Site (root)']
        except Exception as ex:
            eKLogger.log(str(ex))
            return None

    def getVersion(inputServer):
        url = inputServer + API_VERSION
        try:
            r = requests.get(url, verify = False)
            if eKConnector.isResponseSuccess(r.text):
                result = json.loads(r.text)
                return result['result']
            else:
                return None
        except Exception as ex:
            eKLogger.log(str(ex))
            return None