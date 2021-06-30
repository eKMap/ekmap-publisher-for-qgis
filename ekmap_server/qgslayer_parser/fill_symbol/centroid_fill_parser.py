from PyQt5.QtCore import QSize
from .fill_layer_parser import FillLayerParser
from ...ekmap_common import *
from ...ekmap_converter import eKConverter

import hashlib, importlib.util, json
from pathlib import Path

class CentroidFillParser(FillLayerParser):

    def __init__(self, centroidFillLayer, exporter):
        super().__init__(centroidFillLayer)

        file = Path(__file__).resolve()
        parent = file.parent.parent
        spec = importlib.util.spec_from_file_location("eKMap-Publisher-For-QGIS.ekmap_server.qgslayer_parser.symbol_layer_factory", 
            str(parent) + "/symbol_layer_factory.py")
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        subSymbolStyle = []
        for subSymbol in centroidFillLayer.subSymbol():
            borderStyle = foo.SymbolLayerFactory \
                .getLayerParser(subSymbol, exporter)
            subSymbolStyle.extend(borderStyle.parse())

        markerPatternName = json.dumps(subSymbolStyle)
        markerPatternName = hashlib.md5(markerPatternName.encode()).hexdigest()

        dstPath = TEMP_LOCATION + '/' + markerPatternName + '.png'
        sizeUnit = eKConverter.convertRenderUnitValueToName(centroidFillLayer.subSymbol().sizeUnit())
        size = eKConverter.convertUnitToPixel(centroidFillLayer.subSymbol().size(), sizeUnit)
        centroidFillLayer.subSymbol().exportImage(dstPath, 'png', QSize(size, size))
        exporter.externalGraphics.append(dstPath)

        self.styles.append({
            'type': 'symbol',
            'layout': {
                'icon-image': markerPatternName,
                'symbol-placement': 'point'
            },
            'paint': {
                'icon-opacity': centroidFillLayer.subSymbol().opacity()
            }
        })