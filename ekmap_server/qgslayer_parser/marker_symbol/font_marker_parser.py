from .marker_layer_parser import MarkerLayerParser

class FontMarkerParser(MarkerLayerParser):

    def __init__(self, fontMarkerLayer):
        super().__init__(fontMarkerLayer)

        shapeConfig = self.DEFAULT_MARKER_CONFIG
        shapeConfig['marker-name'] = 'font'
        self.initMarkerStyle(fontMarkerLayer, shapeConfig)