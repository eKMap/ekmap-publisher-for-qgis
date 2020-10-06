import math

MAX_SCALE_PER_PIXEL = 156543.04
INCHES_PER_METER = 39.37

# Hàm đổi đơn vị về Pixel dựa vào hàm tính của GIS CLOUD
def convertUnitToPixel(outputDpi, value, unit):
    scalePixel = outputDpi / 72
    value = float(str(value))
    switcher = {
        "MM": 3.78 * scalePixel * value,
        "Point": 1.33 * scalePixel * value,
        "Inch": 96 * scalePixel * value,
    }
    return switcher.get(unit, value)

# Hàm đổi scale sang level dựa vào hàm tính của GIS CLOUD
def convertScaleToLevel(iface, scale):
    level = 0
    physicalDpiX = iface.mainWindow().physicalDpiX()
    factor = physicalDpiX * MAX_SCALE_PER_PIXEL * INCHES_PER_METER
    if scale > 0:
        level = int(round(math.log((factor / scale), 2), 0))
    # ở version ISQIS3 thì min/max để thứ tự như này
    # ở QGis2 thì cần phải set ngược lại
    return level

def convertStrokeTypeToVieType(strokeType):
    switcher = {
        "dash": "dash",
        "solid": "solid",
        "dash dot": "dashdot",
        "dot": "dot",
        # không support "dash dot dot"
        # thiếu "longdash"
        # thiếu "longdashdot"
    }
    return switcher.get(strokeType, "solid")

def convertGraphicNameToVieType(name):
    switcher = {
        "circle": "circle",
        "square": "square",
        "star": "star",
        "cross": "x", # ép dấu + về dấu x
        "cross2": "x", # dấu x
        "cross_fill": "cross", # dấu thập
        "triangle": "triangle",
        "equilateral_triangle": "triangle", # ép tam giác đều về tam giác thường
    }
    return switcher.get(name, "circle")

def convertLayerToGeoType(type):
    switcher = {
        0: "POINT",
        1: "LINESTRING",
        2: "POLYGON",
        3: "UNKNOWN",
        4: "NULL",
    }
    return switcher.get(type, None)

def convertExtensionToName(extension):
    switcher = {
        "shp": "Shapefile",
        "geojson": "GeoJSON",
        "xyz": "ZXY",
    }
    return switcher.get(extension, extension)

def convertDataType(dataType):
    switcher = {
        "String": "nvarchar",
        "Real": "float",
        "float8": "float",
        "int4": "int",
        "int identity": "int",
        "Integer": "int",
        "Integer64": "int",
        "Date": "datetime",
        "Logic": "bit",
    }
    return switcher.get(dataType, dataType)