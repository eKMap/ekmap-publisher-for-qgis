from ..symbol_layer_parser import SymbolLayerParser
from ...ekmap_converter import eKConverter

class LineLayerParser(SymbolLayerParser):

    def __init__(self, lineLayer):
        # Inherit styles and properties attribute from parent
        super().__init__(lineLayer)
        self.outlineWidth = self.properties.get('line_width', 1)
        if self.outlineWidth != 0:
            outlineWidthUnit = self.properties.get('line_width_unit')
            self.outlineWidth = float(eKConverter.convertUnitToPixel(self.outlineWidth, outlineWidthUnit))
        
    def initBaseLineConfig(self, lineLayer):
        lineConfig = {}
        lineStyle = self.properties.get("line_style")
        if lineStyle == 'no':
            lineConfig['visibility'] = 'none'
        else:
            lineConfig['visibility'] = 'visible'

        lineConfig['line-width'] = self.outlineWidth
        lineConfig['line-color'] = lineLayer.color().name()
        lineConfig['line-opacity'] = lineLayer.color().alpha() / 255
        lineConfig['line-dasharray'] = eKConverter.convertStrokeTypeToDashArray(lineStyle, self.outlineWidth)

        lineConfig['line-cap'] = eKConverter.convertLineCap(self.properties.get('capstyle'))
        lineConfig['line-join'] = eKConverter.convertLineJoin(self.properties.get('joinstyle'))

        return lineConfig