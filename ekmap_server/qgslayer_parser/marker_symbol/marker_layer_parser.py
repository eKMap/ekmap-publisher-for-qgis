from ..symbol_layer_parser import SymbolLayerParser
from ...ekmap_converter import eKConverter

class MarkerLayerParser(SymbolLayerParser):

    def __init__(self, markerLayer):
        # Inherit styles and properties atribute from parent
        super().__init__(markerLayer)
        
        self.outlineWidth = self.properties.get('outline_width', 0)
        if self.outlineWidth != 0:
            outlineWidthUnit = self.properties.get('outline_width_unit')
            self.outlineWidth = int(eKConverter.convertUnitToPixel(self.outlineWidth, outlineWidthUnit))

        size = round(float(self.properties.get("size", 1)))
        if size is not None:
            sizeUnit = self.properties.get("size_unit")
            size = int(eKConverter.convertUnitToPixel(size, sizeUnit))

        # size is equivalent to width
        self.width = size
        # aspect ratio = width / height
        fixedAspectRatio = float(self.properties.get('fixedAspectRatio', 0))
        if fixedAspectRatio == 0: # case width = height
            fixedAspectRatio = 1
        self.height = round(size * fixedAspectRatio)

        self.DEFAULT_MARKER_CONFIG['marker-width'] = self.width
        self.DEFAULT_MARKER_CONFIG['marker-height'] = self.height

    # To draw this kind of shape
    # present 2 layers: the bigger layer for stroke backward
    # and the smaller layer for fill forward
    # the different size between 2 layers is the stroke width of shape
    def initMarkerStyle(self, markerLayer, shapeConfig):
        # Draw forward first
        shapeConfig['marker-color'] = markerLayer.color().name()
        styleFill = self.exporteKMarkerLayerFormat(shapeConfig)

        if self.outlineWidth != 0:
            # Draw backward
            shapeConfig['marker-color'] = markerLayer.strokeColor().name()
            shapeConfig['marker-width'] = self.width + self.outlineWidth
            shapeConfig['marker-height'] = self.height + self.outlineWidth
            styleStroke = self.exporteKMarkerLayerFormat(shapeConfig)
            self.styles.append(styleStroke)

        # Push forward last        
        self.styles.append(styleFill)