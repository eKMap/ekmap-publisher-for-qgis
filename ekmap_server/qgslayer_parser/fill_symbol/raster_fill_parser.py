from .fill_layer_parser import FillLayerParser
from ...ekmap_converter import eKConverter
from ...ekmap_common import *

import hashlib, shutil

class RasterFillParser(FillLayerParser):
    def __init__(self, rasterFillParser, exporter) -> None:
        super().__init__(rasterFillParser)

        imagePath = rasterFillParser.imageFilePath()
        imageName = hashlib.md5(imagePath.encode()).hexdigest()

        imageWidth = rasterFillParser.width()
        if imageWidth > 0:
            imageWidthUnit = eKConverter.convertRenderUnitValueToName(rasterFillParser.widthUnit())
            imageWidth = int(eKConverter.convertUnitToPixel(imageWidth, imageWidthUnit))
            imageName = imageName \
                + '_W' + str(imageWidth) \
                + '_H' + str(imageWidth)
        
        rotation = int(rasterFillParser.angle())
        if rotation > 0:
            imageName = imageName \
                + '_R' + str(rotation)

        opacity = float(self.properties.get('alpha', 1))

        dstPath = TEMP_LOCATION + '/' + imageName + '.png'
        shutil.copy2(imagePath, dstPath)
        exporter.externalGraphics.append(dstPath)

        fillConfig = {
            'fill-pattern': imageName,
            'fill-opacity': opacity
        }
        self.styles.append(self.exportFillLayerFormat(fillConfig))