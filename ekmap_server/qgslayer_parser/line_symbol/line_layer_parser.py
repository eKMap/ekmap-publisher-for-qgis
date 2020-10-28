from ..symbol_layer_parser import SymbolLayerParser
from ...ekmap_converter import eKConverter

class LineLayerParser(SymbolLayerParser):

    def __init__(self, lineLayer):
        # Inherit styles and properties atribute from parent
        super().__init__(lineLayer)
        self.outlineWidth = self.properties.get('line_width', 1)
        if self.outlineWidth != 0:
            outlineWidthUnit = self.properties.get('line_width_unit')
            self.outlineWidth = float(eKConverter.convertUnitToPixel(self.outlineWidth, outlineWidthUnit))
        
    def initBaseLineConfig(self, lineLayer):
        lineConfig = {}
        lineConfig['line-width'] = self.outlineWidth
        lineConfig['line-color'] = lineLayer.color().name()
        lineConfig['line-opacity'] = lineLayer.color().alpha() / 255
        lineStyle = self.properties.get("line_style")
        lineConfig['line-dasharray'] = eKConverter.convertStrokeTypeToVieType(lineStyle)

        lineConfig['line-cap'] = self.properties.get('capstyle')
        lineConfig['line-join'] = self.properties.get('joinstyle')

        return lineConfig