from .fill_layer_parser import FillLayerParser

class SVGFillParser(FillLayerParser):
    
    def __init__(self, simpleFillLayer):
        super().__init__(simpleFillLayer)

        