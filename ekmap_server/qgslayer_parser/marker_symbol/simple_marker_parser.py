from .marker_layer_parser import MarkerLayerParser
from ...ekmap_converter import eKConverter

# This is a parser for simple geometry
# like square, circle, triangle, star, pentagon, hexagon,...
class SimpleMarkerParser(MarkerLayerParser):

    # Missing case outline style no or outline width = 0
    # which means there is no layer backward
    # need recode in here
    def __init__(self, simpleMarkerLayer):
        super().__init__(simpleMarkerLayer)

        # Get the name of shape
        markerName = str(self.properties.get('name'))
        # If the name of shape is empty
        # draw the default shape
        if markerName is None:
            # do something here
            markerName = 'circle'
        # Else, read the shape
        else:
            # Convert the shape of QGIS to shape of eKMap
            # If eKMap not support, default convert to CIRCLE
            markerName = eKConverter.convertGraphicNameToVieType(markerName)
            
        shapeConfig = self.DEFAULT_MARKER_CONFIG
        shapeConfig['marker-name'] = markerName
        shapeConfig['marker-image'] = None
        self.initMarkerStyle(simpleMarkerLayer, shapeConfig)