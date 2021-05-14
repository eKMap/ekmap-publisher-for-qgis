from .marker_symbol.simple_marker_parser import SimpleMarkerParser
from .marker_symbol.raster_marker_parser import RasterMarkerParser
from .marker_symbol.svg_marker_parser import SvgMarkerParser
from .marker_symbol.font_marker_parser import FontMarkerParser
from .line_symbol.simple_line_parser import SimpleLineParser
from .fill_symbol.simple_fill_parser import SimpleFillParser
from .fill_symbol.svg_fill_parser import SVGFillParser
from .fill_symbol.raster_fill_parser import RasterFillParser
from .fill_symbol.point_fill_parser import PointFillParser
from .fill_symbol.line_fill_parser import LineFillParser

class SymbolLayerFactory():

    def getLayerParser(symbolLayer, exporter):
        layerType = symbolLayer.layerType()
        # parser = {
        #     'SimpleMarker': SimpleMarkerParser(symbolLayer),
        #     'RasterMarker': RasterMarkerParser(symbolLayer),
        #     'SvgMarker': SvgMarkerParser(symbolLayer),
        #     'FontMarker': FontMarkerParser(symbolLayer),
        #     'SimpleLine': SimpleLineParser(symbolLayer),
        #     'SimpleFill': SimpleFillParser(symbolLayer, exporter),
        #     'SVGFill': SVGFillParser(symbolLayer, exporter),
        #     'RasterFill': RasterFillParser(symbolLayer, exporter),
        #     'PointPatternFill': PointFillParser(symbolLayer, exporter),
        #     'LinePatternFill': LineFillParser(symbolLayer, exporter)
        # }
        # return parser.get(layerType, None)
        if layerType ==  'SimpleMarker':
            return SimpleMarkerParser(symbolLayer)
        elif layerType == 'RasterMarker':
            return RasterMarkerParser(symbolLayer)
        elif layerType == 'SvgMarker':
            return SvgMarkerParser(symbolLayer)
        elif layerType == 'FontMarker':
            return FontMarkerParser(symbolLayer)
        elif layerType == 'SimpleLine':
            return SimpleLineParser(symbolLayer)
        elif layerType == 'SimpleFill':
            return SimpleFillParser(symbolLayer, exporter)
        elif layerType == 'SVGFill':
            return SVGFillParser(symbolLayer, exporter)
        elif layerType == 'RasterFill':
            return RasterFillParser(symbolLayer, exporter)
        elif layerType == 'PointPatternFill':
            return PointFillParser(symbolLayer, exporter)
        elif layerType == 'LinePatternFill':
            return LineFillParser(symbolLayer, exporter)
        return None