from .line_layer_parser import LineLayerParser

class SimpleLineParser(LineLayerParser):

    def __init__(self, simpleLineParser):
        super().__init__(simpleLineParser)

        _lineConfig = self.DEFAULT_LINE_CONFIG
        self.initLineStyle(simpleLineParser, _lineConfig)