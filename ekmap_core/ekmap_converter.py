import math

class eKConverter():

    MAX_SCALE_PER_PIXEL = 156543.04
    INCHES_PER_METER = 39.37

    IFACE = None

    # Convert render unit value to unit name
    # Refer: https://qgis.org/api/classQgsUnitTypes.html#ae04d6633d29996dbc2ab07e737a04adf
    def convertRenderUnitValueToName(value):
        switcher = {
            '0': 'MM',
            # '1': 'MapUnit', # Not supported
            # '2': 'Pixel',
            # '3': 'Percentage', # Not supported
            '4': 'Point',
            '5': 'Inches',
            # '6': 'UnknownUnit', # Not supported
            # '7': 'MetersInMapUnit', # Not supported
        }
        return switcher.get(str(value), 'Pixel')

    # Convert to pixel method
    # Refer: GIS CLOUD plugin
    def convertUnitToPixel(value, unit):
        scalePixel = eKConverter.IFACE.mapCanvas().mapSettings().outputDpi() / 72
        # scalePixel = 96 / 72

        value = float(str(value))
        switcher = {
            "MM": 3.78 * scalePixel * value,
            "Point": 1.33 * scalePixel * value,
            "Inch": 96 * scalePixel * value,
        }
        return switcher.get(unit, value)

    # Convert scale to zoom level method
    # Refer: GIS CLOUD plugin
    def convertScaleToLevel(scale):
        level = 0
        physicalDpiX = eKConverter.IFACE.mainWindow().physicalDpiX()
        factor = physicalDpiX * eKConverter.MAX_SCALE_PER_PIXEL * eKConverter.INCHES_PER_METER
        if scale > 0:
            level = int(round(math.log((factor / scale), 2), 0))
        # In version ISQIS3 min/max in this order
        # In QGis2 it is reverse
        return level

    def convertStrokeTypeToDashArray(strokeType, strokeWidth):
        dotWidth = strokeWidth
        dashWidth = strokeWidth * 3
        spacing = strokeWidth * 3 / 2

        switcher = {
            "dash": [dashWidth, spacing], # "dash",
            "dash dot": [dashWidth, spacing, dotWidth, spacing], # "dashdot",
            "dot": [dotWidth, spacing], # "dot",
            "dash dot dot": [dashWidth, spacing, dotWidth, spacing, dotWidth, spacing],
        }
        return switcher.get(strokeType, []) # None = solid

    def convertGraphicName(name):
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

    def getExtension(provider):
        extension = {
            'geojson': 'json'
        }
        return extension.get(provider, provider)

    def convertExtensionToName(provider):
        switcher = {
            "shp": "Shapefile",
            "geojson": "GeoJSON",
            "xyz": "ZXY",
            "gdb": "GDB",
            "sqlite": "SQLite",
            "tif": "GeoTiff"
        }
        return switcher.get(provider, None)

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

    def convertLabelPlacement(placementValue):
        switcher = {
            # 0: "around-point",
            # 1: "over-point",
            2: "line", # Parallel
            # 3: "curved",
            4: "point", # Horizontal
            5: "line", #"free",
            # 6: "ordered-position-around-point",
            7: "line", #"perimeter-curved",
            # 8: "outside-polygon",
        }
        return switcher.get(placementValue, "point")

    def convertLineJoin(lineJoin):
        switcher = {
            'miter': 'miter',
            'round': 'round',
            'bevel': 'bevel'
        }
        return switcher.get(lineJoin, 'miter')

    def convertLineCap(lineCap):
        switcher = {
            'flat': 'butt',
            'round': 'round',
            'square': 'square'
        }
        return switcher.get(lineCap, 'butt')

    def convertQuadrantToAnchor(quadOffset):
        switcher = {
            0: 'bottom-right',
            1: 'bottom',
            2: 'bottom-left',
            3: 'right',
            4: 'center',
            5: 'left',
            6: 'top-right',
            7: 'top',
            8: 'top-left'
        }
        return switcher.get(quadOffset, 'bottom')