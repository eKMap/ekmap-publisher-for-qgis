from .fill_layer_parser import FillLayerParser
from ...ekmap_converter import eKConverter

class SimpleFillParser(FillLayerParser):

    def __init__(self, simpleFillLayer):
        super().__init__(simpleFillLayer)

        fillConfig = self.DEFAULT_FILL_CONFIG
        fillConfig['fill-color'] = simpleFillLayer.color().name()
        fillConfig['fill-opacity'] = simpleFillLayer.color().alpha() / 255

        fillStyleLayer = self.exportFillLayerFormat(fillConfig)
        self.styles.append(fillStyleLayer)

        if self.outlineWidth != 0:
            lineConfig = self.DEFAULT_LINE_CONFIG
            lineConfig['line-width'] = self.outlineWidth
            lineConfig['line-join'] = self.properties.get('joinstyle')
            lineConfig['line-color'] = simpleFillLayer.strokeColor().name()
            lineConfig['line-opacity'] = simpleFillLayer.strokeColor().alpha() / 255

            outlineStyle = self.properties.get("outline_style")
            lineConfig['line-dasharray'] = eKConverter.convertStrokeTypeToVieType(outlineStyle)

            lineStyleLayer = self.exportLineLayerFormat(lineConfig)
            self.styles.append(lineStyleLayer)