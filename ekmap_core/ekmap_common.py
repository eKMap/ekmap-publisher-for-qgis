import os, shutil

TEMP_LOCATION = str(os.path.dirname(os.path.dirname(__file__))) + '/tmp'

LOGGER_NAME = 'eKLogger'
LOGGER_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
LOGGER_DIR = str(os.path.dirname(os.path.dirname(__file__))) + '/log.txt'

SETTING_TOKEN = "ekmap_server_publisher/token"
SETTING_COOKIES = "ekmap_server_publisher/cookies"
SETTING_USERNAME = "ekmap_server_publisher/username"
SETTING_SERVER = "ekmap_server_publisher/server"
SETTING_MAPPING = "ekmap_server_publisher/mapping"

API_LOGIN = "/api/TokenAuth/Authenticate"
API_UPLOAD = "/ekmapserver/rest/services/Package/upload"
API_INFO = "/ekmapserver/rest/services/Package/info"
API_PUBLISH = "/ekmapserver/rest/services/Map/Publish"
API_VERSION = "/ekmapserver/rest/services/version"
API_COLLECTION = "/ekmapserver/rest/services/collection"

REQUIRE_MIN_SERVER_VERSION = 'v1.0.0'

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

    def urlParamToMap(urlParam):
        params = urlParam.split("&")
        result = {}

        for param in params:
            paramSplit = param.split("=")
            if len(paramSplit) == 2:
                result[paramSplit[0]] = paramSplit[1]
        
        return result

    def rgbaToHex(rgba):
        r,g,b,a = rgba.split(',')
        colorR = int(r), int(g), int(b), int(a)
        colorHex = '#{:02x}{:02x}{:02x}'.format(*colorR)
        return colorHex

    def getTransparentFromRGBA(rgba):
        r,g,b,a = rgba.split(',')
        transparent = int(a) / 255
        return transparent