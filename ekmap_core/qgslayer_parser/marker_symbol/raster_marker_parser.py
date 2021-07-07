from .marker_layer_parser import MarkerLayerParser

# This is a parser for raster image marker
class RasterMarkerParser(MarkerLayerParser):

    def __init__(self, rasterMarkerLayer):
        super().__init__(rasterMarkerLayer)

        # For this marker
        # copy information of image 
        # and encapsulate into eKMarkerLayer 
        shapeConfig = self.DEFAULT_MARKER_CONFIG
        shapeConfig['marker-name'] = 'raster-image'
        # Get the image path        
        shapeConfig['marker-image'] = self.properties.get('imageFile')
        # self.externalGraphic.append(self.properties.get('imageFile'))
        self.initMarkerStyle(rasterMarkerLayer, shapeConfig)