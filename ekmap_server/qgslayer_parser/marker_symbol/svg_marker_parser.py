from .marker_layer_parser import MarkerLayerParser

# This is a parser for svg image
class SvgMarkerParser(MarkerLayerParser):

    def __init__(self, svgMarkerParser):
        super().__init__(svgMarkerParser)

        # Except image information like RasterMarker
        # this marker contains some paint information to re-draw
        _shapeConfig = self.DEFAULT_MARKER_CONFIG
        _shapeConfig['marker-name'] = 'svg-image'
        # Get the image path        
        _shapeConfig['marker-image'] = self.properties.get('name')
        self.initMarkerStyle(svgMarkerParser, _shapeConfig)