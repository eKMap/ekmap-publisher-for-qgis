from .fill_layer_parser import FillLayerParser
from ...ekmap_common import *
from ...ekmap_converter import eKConverter
from ...ekmap_logger import eKLogger

from PIL import Image, ImageDraw
import hashlib

DEFAULT_SIZE = 10

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
            patternName = fillStyle + fillColor
            patternName = hashlib.md5(patternName.encode()).hexdigest()
            dstPath = TEMP_LOCATION + '/' + patternName + '.png'
            exporter.externalGraphics.append(dstPath)
            SimpleFillParser.__drawLinePattern(fillStyle, fillColor, dstPath)
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

    def __getPattern(fillStyle):
        pattern = {
            'horizontal': [(0, DEFAULT_SIZE/2), (DEFAULT_SIZE, DEFAULT_SIZE/2)],
            'vertical': [(DEFAULT_SIZE/2, 0), (DEFAULT_SIZE/2, DEFAULT_SIZE)],
            'cross': [(0, DEFAULT_SIZE/2), (DEFAULT_SIZE, DEFAULT_SIZE/2), 
                        (DEFAULT_SIZE/2, DEFAULT_SIZE/2), 
                        (DEFAULT_SIZE/2, 0), (DEFAULT_SIZE/2, DEFAULT_SIZE)],
            'b_diagonal': [(DEFAULT_SIZE, 0), (0, DEFAULT_SIZE)],
            'f_diagonal': [(0,0), (DEFAULT_SIZE, DEFAULT_SIZE)],
            'diagonal_x': [(DEFAULT_SIZE, 0), (0, DEFAULT_SIZE), 
                            (DEFAULT_SIZE/2, DEFAULT_SIZE/2), 
                            (0, 0), (DEFAULT_SIZE, DEFAULT_SIZE)],
            'dense1': None,
            'dense2': None,
            'dense3': None,
            'dense4': None,
            'dense5': None,
            'dense6': None,
            'dense7': None
        }
        return pattern.get(fillStyle, None)

    def __drawLinePattern(fillStyle, color, dstPath):
        xy = SimpleFillParser.__getPattern(fillStyle)
        if xy is not None:
            img = Image.new('RGBA', (DEFAULT_SIZE, DEFAULT_SIZE), (255, 0, 0, 0))
            drawImg = ImageDraw.Draw(img)
            drawImg.line(xy, fill=color ,width=1)
            img.save(dstPath, 'PNG')