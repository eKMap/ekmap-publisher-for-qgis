from ..ekmap_converter import eKConverter

class SimpleLabelParser():

    def __init__(self, layer):
        self.labeling = layer.labeling()
    
    def read(self):
        if self.labeling is None:
            return None
        else:
            self.settings = self.labeling.settings()

            # styleLayer = self.readZoomLevel()
            styleLabel = self.readTextStyle()
            # self.readBackground()
            # self.readPlacement()

            return styleLabel

    def readTextStyle(self):
        labelFormat = self.settings.format()

        field = self.settings.fieldName
        xOffset = float(self.settings.xOffset)
        yOffset = float(self.settings.yOffset)
        
        fontName = labelFormat.font().family()
        fontColor = labelFormat.color().name()
        fontStyle = labelFormat.namedStyle()

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
        placement = self.settings.placement
        placement = eKConverter.convertLabelPlacement(placement)

        # Export information here
        labelPaint = {
            'text-color': fontColor,
            'text-halo-color': strokeColor,
            'text-halo-width': strokeWidth,
        }
        labelLayout = {
            'text-font': [fontName],
            'text-field': '{' + field + '}',
            'text-size':  fontSize,
            'text-offset': [xOffset, yOffset],
            'symbol-placement': placement,
        }
        return {
            'type': 'symbol',
            'paint': labelPaint,
            'layout': labelLayout
        }

    def readZoomLevel(self):
        minLevel = 0
        maxLevel = 22
        if self.settings.scaleVisibility:
            minLevel = eKConverter.convertScaleToLevel(scale = self.settings.minimumScale)
            if self.settings.maximumScale != 0:
                maxLevel = eKConverter.convertScaleToLevel(scale = self.settings.maximumScale)

        # Export information here
        return {
            'minLevel': minLevel,
            'maxLevel': maxLevel,
            'visible': True
        }

    # Refer: https://qgis.org/pyqgis/3.0/core/Text/QgsTextBackgroundSettings.html
    def readBackground(self):
        background = self.settings().format().background()
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
            sizeType = background.sizeType()

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
                fillColor = background.fillColor().name()
                strokeColor = background.strokeColor().name()
                strokeWidth = background.strokeWidth()
                strokeWidthUnit = background.strokeWidthUnit()

                # convert the width to pixel
                strokeWidth = eKConverter.convertUnitToPixel(value = strokeWidth, unit = strokeWidthUnit)

            # Export information here
            # ...
    
    def readPlacement(self):
        layerType = self.settings.layerType()
        # Refer: https://qgis.org/api/classQgsWkbTypes.html#a60e72c2f73cb07fdbcdbc2d5068b5d9c
        # POINT
        if layerType == 0:
            # Point has: Cartographic, around point, offset from point
            a = 1
        # LINESTRING
        elif layerType == 1:
            # Line has: Parallel, curved, horizontal
            a = a
        # POLYGON
        elif layerType == 2:
            # Polygon has: Offset from point, horizontal,
            # around centroid, free, using perimeter,
            # using perimeter (curved), outside polygons
            a = 1