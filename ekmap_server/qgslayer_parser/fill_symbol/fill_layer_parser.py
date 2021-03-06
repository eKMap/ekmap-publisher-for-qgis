from ..symbol_layer_parser import SymbolLayerParser
from ...ekmap_converter import eKConverter

class FillLayerParser(SymbolLayerParser):

    def __init__(self, fillLayer):
        # Inherit styles and properties attribute from parent
        super().__init__(fillLayer)

        self.outlineWidth = self.properties.get('outline_width', 0.2)
        if self.outlineWidth == 0:
            self.outlineWidth = 0.2
        outlineWidthUnit = self.properties.get('outline_width_unit')
        self.outlineWidth = float(eKConverter.convertUnitToPixel(self.outlineWidth, outlineWidthUnit))