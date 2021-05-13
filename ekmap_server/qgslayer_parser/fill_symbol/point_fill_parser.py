from PyQt5.QtCore import QSize
from .fill_layer_parser import FillLayerParser
from ...ekmap_common import *
from ...ekmap_converter import eKConverter

import hashlib, importlib.util, json
from pathlib import Path 

class PointFillParser(FillLayerParser):

    def __init__(self, pointFillLayer, exporter):
        super().__init__(pointFillLayer)

        dx = pointFillLayer.distanceX()
        dxUnit = eKConverter.convertRenderUnitValueToName(pointFillLayer.distanceXUnit())
        dx  = int(eKConverter.convertUnitToPixel(dx, dxUnit))

        dy = pointFillLayer.distanceY()
        dyUnit = eKConverter.convertRenderUnitValueToName(pointFillLayer.distanceYUnit())
        dy = int(eKConverter.convertUnitToPixel(dy, dyUnit))

        file = Path(__file__).resolve()
        parent = file.parent.parent
        spec = importlib.util.spec_from_file_location("eKMap-Publisher-For-QGIS.ekmap_server.qgslayer_parser.symbol_layer_factory", 
            str(parent) + "/symbol_layer_factory.py")
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        subSymbolStyle = []
        for subSymbol in pointFillLayer.subSymbol():
            borderStyle = foo.SymbolLayerFactory \
                .getLayerParser(subSymbol, exporter)
            subSymbolStyle.extend(borderStyle.parse())
        
        markerPatternName = json.dumps(subSymbolStyle)
        markerPatternName = hashlib.md5(markerPatternName.encode()).hexdigest()
        markerPatternName = markerPatternName \
            + '_Dx' + str(dx) \
            + '_Dy' + str(dy)
        dstPath = TEMP_LOCATION + '/' + markerPatternName + '.png'
        sizeUnit = eKConverter.convertRenderUnitValueToName(pointFillLayer.subSymbol().sizeUnit())
        size = eKConverter.convertUnitToPixel(pointFillLayer.subSymbol().size(), sizeUnit)
        pointFillLayer.subSymbol().exportImage(dstPath, 'png', QSize(size, size))
        exporter.externalGraphics.append(dstPath)

        fillConfig = {
            'fill-pattern': markerPatternName,
            'fill-opacity': 1
        }
        fillStyleLayer = self.exportFillLayerFormat(fillConfig)
        self.styles.append(fillStyleLayer)