from .marker_symbol.simple_marker_parser import SimpleMarkerParser
from .marker_symbol.raster_marker_parser import RasterMarkerParser
from .marker_symbol.svg_marker_parser import SvgMarkerParser
from .line_symbol.simple_line_parser import SimpleLineParser
from .fill_symbol.simple_fill_parser import SimpleFillParser

class SymbolLayerFactory():

    def getLayerParser(symbolLayer):
        layerType = symbolLayer.layerType()
        if layerType ==  'SimpleMarker':
            return SimpleMarkerParser(symbolLayer)
        elif layerType == 'RasterMarker':
            return RasterMarkerParser(symbolLayer)
        elif layerType == 'SvgMarker':
            return SvgMarkerParser(symbolLayer)
        elif layerType == 'SimpleLine':
            return SimpleLineParser(symbolLayer)
        elif layerType == 'SimpleFill':
            return SimpleFillParser(symbolLayer)
        return None