from .fill_layer_parser import FillLayerParser
from ...ekmap_common import *
from ...ekmap_converter import eKConverter

CURRENT_PATH = str(os.path.dirname(__file__))

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
            # Need to replace because '_' is splitter
            patternName = fillStyle.replace('_','') \
                + "_C" + fillColor
            dstPath = TEMP_LOCATION + '/' + patternName + '.png'
            shutil.copy2(CURRENT_PATH + '/img/' + fillStyle + '.png', dstPath)
            exporter.externalGraphics.append(dstPath)

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
            lineConfig['line-dasharray'] = eKConverter.convertStrokeTypeToDashArray(outlineStyle, self.outlineWidth)

            lineStyleLayer = self.exportLineLayerFormat(lineConfig)
            self.styles.append(lineStyleLayer)