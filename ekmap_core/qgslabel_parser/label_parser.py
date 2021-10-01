from PyQt5.QtWidgets import QMainWindow
from ..ekmap_converter import eKConverter
import re
from qgis.core import QgsMessageLog

class LabelParser:

    def __init__(self, labeling):
        self.labeling = labeling

    def _readTextStyle(self, settings):
        labelFormat = settings.format()

        field = settings.fieldName
        finds = re.findall(r"\((.*?)\)", field)
        if (len(finds) == 1):
            field = finds[0]

        xOffset = float(settings.xOffset)
        yOffset = float(settings.yOffset)
        offsetUnit = settings.offsetUnits
        xOffset = eKConverter.convertUnitToPixel(value=xOffset, unit=offsetUnit)
        yOffset = eKConverter.convertUnitToPixel(value=yOffset, unit=offsetUnit)
        if xOffset == 0 and yOffset == 0:
            yOffset = -1.5


        fontName = labelFormat.font().family()
        fontColor = labelFormat.color().name()
        # fontStyle = labelFormat.namedStyle()

        fontSize = float(labelFormat.size())
        fontSizeUnit = labelFormat.sizeUnit()
        # convert the size to pixel
        fontSize = eKConverter.convertUnitToPixel(value = fontSize, unit = fontSizeUnit)

        # Refer: https://qgis.org/api/classQgsTextBufferSettings.html
        strokeColor = labelFormat.buffer().color().name()
        strokeWidth = labelFormat.buffer().size()
        strokeWidthUnit = labelFormat.buffer().sizeUnit()
        # convert the width to pixel
        strokeWidth = eKConverter.convertUnitToPixel(value = strokeWidth, unit = strokeWidthUnit)

        # TEMP
        placement = settings.placement
        placement = eKConverter.convertLabelPlacement(placement)

        # Export information here
        labelPaint = {
            'text-color': fontColor,
            'text-halo-color': strokeColor,
            'text-halo-width': strokeWidth,
        }
        labelLayout = {
            'text-font': [fontName],
            'text-field': ["get", field],
            'text-size':  fontSize,
            'text-offset': [xOffset, yOffset],
            'text-anchor': self.__getAnchor(settings),
            'text-rotate': self.__getRotation(settings),
            'symbol-placement': placement,
        }

        return {
            'type': 'symbol',
            'paint': labelPaint,
            'layout': labelLayout
        }

    def readZoomLevel(self, settings):
        minLevel = 0
        maxLevel = 22
        if settings.scaleVisibility:
            minLevel = eKConverter.convertScaleToLevel(scale = settings.minimumScale)
            if settings.maximumScale != 0:
                maxLevel = eKConverter.convertScaleToLevel(scale = settings.maximumScale)

        # Export information here
        return {
            'minLevel': minLevel,
            'maxLevel': maxLevel,
            'visible': True
        }

    # Refer: https://qgis.org/pyqgis/3.0/core/Text/QgsTextBackgroundSettings.html
    def readBackground(self, settings):
        background = settings().format().background()
        if background.enabled():
            # Identify the type of background
            # Refer: https://qgis.org/api/classQgsTextBackgroundSettings.html#a91794614626586cc1f3d861179cc26f9
            # basic shape like: rectangle = 0, 
            # square = 1, eclipse = 2, circle = 3
            # or svg image = 4
            # or marker symbol = 5
            backgroundType = background.type()

            # Identify the type of size 
            # Refer: https://qgis.org/api/classQgsTextBackgroundSettings.html#a45798d989b02e1dfcad9a6f1db4cd153
            # 1 = buffer: the size of background = size of label + buffer
            # 2 = fixed: the size of background = fixed
            # 3 = percent: determine by the size of text size
            # sizeType = background.sizeType()

            # Get the size information
            # this return QSizeF object
            size = background.size()
            width = size.width()
            height = size.height()

            # Identify the unit of size
            sizeUnit = background.sizeUnit()
            # then convert the size to pixel
            width = eKConverter.convertUnitToPixel(value = width, unit = sizeUnit)
            height = eKConverter.convertUnitToPixel(value = height, unit = sizeUnit)

            # Get the fill and stroke
            # apply for basic shape only
            if backgroundType < 4:
                # fillColor = background.fillColor().name()
                # strokeColor = background.strokeColor().name()
                strokeWidth = background.strokeWidth()
                strokeWidthUnit = background.strokeWidthUnit()

                # convert the width to pixel
                strokeWidth = eKConverter.convertUnitToPixel(value = strokeWidth, unit = strokeWidthUnit)

            # Export information here
            # ...
    
    def readPlacement(self, settings):
        layerType = settings.layerType()
        # Refer: https://qgis.org/api/classQgsWkbTypes.html#a60e72c2f73cb07fdbcdbc2d5068b5d9c
        # POINT
        if layerType == 0:
            # Point has: Cartographic (6), 
            # around point (0), 
            # offset from point (1)
            a = 1
        # LINESTRING
        elif layerType == 1:
            # Line has: Parallel, curved, horizontal
            a = 2
        # POLYGON
        elif layerType == 2:
            # Polygon has: Offset from point, horizontal,
            # around centroid, free, using perimeter,
            # using perimeter (curved), outside polygons
            a = 3

    def __getAnchor(self, settings):
        placement = settings.placement

        # Only offset from point has Anchor
        if placement == 1:
            quadOffset = settings.quadOffset
            return eKConverter.convertQuadrantToAnchor(quadOffset)
        # Other set default
        else:
            return 'bottom'

    def __getRotation(self, settings):
        # In-case user defined rotation:
        definedProperties = settings.dataDefinedProperties()
        LABEL_ROTATION = 96
        rotationProperty = definedProperties.property(LABEL_ROTATION)
        if rotationProperty.isActive():
            fieldBase = rotationProperty.field()
            return ['get', fieldBase]
        else:
            placement = settings.placement
            # Only offset from point has Rotation
            if placement == 1:
                return settings.angleOffset
            else:
                return 0
  