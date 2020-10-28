from .marker_layer_parser import MarkerLayerParser

# This is a parser for svg image
class SvgMarkerParser(MarkerLayerParser):

    def __init__(self, svgMarkerParser):
        super().__init__(svgMarkerParser)

        # Except image information like RasterMarker
        # this marker contains some paint information to re-draw
        shapeConfig = self.DEFAULT_MARKER_CONFIG
        shapeConfig['marker-name'] = 'svg-image'
        # Get the image path        
        shapeConfig['marker-image'] = self.properties.get('name')
        self.externalGraphic.append(self.properties.get('name'))
        self.initMarkerStyle(svgMarkerParser, shapeConfig)