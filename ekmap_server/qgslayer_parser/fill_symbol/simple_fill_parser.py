from .fill_layer_parser import FillLayerParser
from ...ekmap_common import *
from ...ekmap_converter import eKConverter
from ...drawing_helper import DrawingHelper
from ...ekmap_logger import eKLogger

import hashlib

class SimpleFillParser(FillLayerParser):

    def __init__(self, simpleFillLayer, exporter):
        super().__init__(simpleFillLayer)

        fillStyle = self.properties.get('style')
        fillColor = simpleFillLayer.color().name()
        fillConfig = {}

        if fillStyle == 'solid':
            fillConfig['fill-color'] = fillColor
            fillConfig['fill-opacity'] = simpleFillLayer.color().alpha() / 255
        else: # Fill with pattern
            # Export pattern to image
            fillStyle = self.__getPattern(fillStyle)
            if fillStyle is not None:
                patternName = fillStyle + fillColor
                patternName = hashlib.md5(patternName.encode()).hexdigest()
                dstPath = TEMP_LOCATION + '/' + patternName + '.png'
                exporter.externalGraphics.append(dstPath)
                DrawingHelper.drawLinePattern(fillStyle, fillColor, dstPath)
                fillConfig['fill-pattern'] = patternName
                fillConfig['fill-opacity'] = simpleFillLayer.color().alpha() / 255

        fillStyleLayer = self.exportFillLayerFormat(fillConfig)
        self.styles.append(fillStyleLayer)

        if self.properties.get('outline_style') != 'no':
            lineConfig = self.DEFAULT_LINE_CONFIG
            lineConfig['line-width'] = self.outlineWidth
            lineConfig['line-join'] = self.properties.get('joinstyle')
            lineConfig['line-color'] = simpleFillLayer.strokeColor().name()
            lineConfig['line-opacity'] = simpleFillLayer.strokeColor().alpha() / 255

            outlineStyle = self.properties.get("outline_style")
            lineConfig['line-dasharray'] = eKConverter.convertStrokeTypeToVieType(outlineStyle)

            lineStyleLayer = self.exportLineLayerFormat(lineConfig)
            self.styles.append(lineStyleLayer)

    def __getPattern(self, fillStyle):
        pattern = {
            'horizontal': 'Horizontal',
            'vertical': 'Vertical',
            'cross': 'Cross',
            'b_diagonal': 'BDiagonal',
            'f_diagonal': 'FDiagonal',
            'diagonal_x': 'DiagonalX',
            'dense1': None,
            'dense2': None,
            'dense3': None,
            'dense4': None,
            'dense5': None,
            'dense6': None,
            'dense7': None
        }
        return pattern.get(fillStyle, None)