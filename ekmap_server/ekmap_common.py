import os, shutil, requests

TEMP_LOCATION = str(os.path.dirname(os.path.dirname(__file__))) + '/tmp'

SETTING_TOKEN = "ekmap_server_publisher/token"
SETTING_USERNAME = "ekmap_server_publisher/username"
SETTING_SERVER = "ekmap_server_publisher/server"
SETTING_MAPPING = "ekmap_server_publisher/mapping"

API_LOGIN = "/api/TokenAuth/Authenticate"
API_UPLOAD = "/gserver/rest/services/mapadmin/uploadpackage"
API_PUBLISH = "/gserver/rest/services/mapadmin/publish"

DEFAULT_STYLE_POINT = {
    "defaultStyle": {
        "title": "Default Point",
        "graphicName": "circle",
        "graphicHeight": 15,
        "graphicWidth": 15,
        "graphicXOffset": 0,
        "graphicYOffset": 0,
        "fillColor": "#000000",
        "fillOpacity": 1.0,
        "strokeWidth": 1,
        "strokeColor": "#000000",
        "strokeOpacity": 1.0,
        "strokeDashType": "solid"
    },
    "rules": []
}

DEFAULT_STYLE_LINE = {
    "defaultStyle": {
        "title": "Default Line",
        "fillColor": "#000000",
        "fillOpacity": 1.0,
        "strokeWidth": 1,
        "strokeColor": "#000000",
        "strokeOpacity": 1.0,
        "strokeDashType": "solid"
    },
    "rules": []
}

DEFAULT_STYLE_POLYGON = {
    "defaultStyle": {
        "title": "Default Polygon",
        "fillColor": "#000000",
        "fillOpacity": 1.0,
        "strokeWidth": 1,
        "strokeColor": "#000000",
        "strokeOpacity": 1.0,
        "strokeDashType": "solid"
    },
    "rules": []
}

DEFAULT_STYLE_LABEL = {
    "labelXOffset": "0",
    "labelYOffset": "0",
    "fontName": "Arial",
    "fontSize": 10,
    "fontColor": "#000000",
    "fontStyle": "",
    "strokeColor": "#FFFFFF",
    "strokeWidth": 1,
    "opacity": 1,
    "level": "0,22"
}

class eKMapCommonHelper:

    def getDefaultStyleBaseOnGeoType(geoType):
        switcher = {
            0: DEFAULT_STYLE_POINT,
            1: DEFAULT_STYLE_LINE,
            2: DEFAULT_STYLE_POLYGON,
        }
        return switcher(geoType, None)

    def cleanTempDir():
        shutil.rmtree(TEMP_LOCATION)
        os.mkdir(TEMP_LOCATION)

    def isConnectionAvailable(url):
        try:
            request = requests.get(url, timeout = 5)
            return True
        except:
            return False

    def urlParamToMap(urlParam):
        params = urlParam.split("&")
        result = {}

        for param in params:
            paramSplit = param.split("=")
            if len(paramSplit) == 2:
                result[paramSplit[0]] = paramSplit[1]
        
        return result