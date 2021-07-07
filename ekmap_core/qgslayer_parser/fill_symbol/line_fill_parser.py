from PyQt5.QtCore import QSize
from .fill_layer_parser import FillLayerParser
from ...ekmap_converter import eKConverter
from ...ekmap_common import *

import hashlib, json, importlib.util
from pathlib import Path 

class LineFillParser(FillLayerParser):

    def __init__(self, lineFillLayer, exporter):
        super().__init__(lineFillLayer)

        spacing = lineFillLayer.distance()
        spacingUnit = eKConverter.convertRenderUnitValueToName(lineFillLayer.distanceUnit())
        spacing = int(eKConverter.convertUnitToPixel(spacing, spacingUnit))

        rotation = int(lineFillLayer.lineAngle())

        file = Path(__file__).resolve()
        parent = file.parent.parent
        spec = importlib.util.spec_from_file_location("eKMap-Publisher-For-QGIS.ekmap_core.qgslayer_parser.symbol_layer_factory", 
            str(parent) + "/symbol_layer_factory.py")
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        subSymbolStyle = []
        for subSymbol in lineFillLayer.subSymbol():
            borderStyle = foo.SymbolLayerFactory \
                .getLayerParser(subSymbol, exporter)
            subSymbolStyle.extend(borderStyle.parse())
        
        linePatternName = json.dumps(subSymbolStyle)
        linePatternName = hashlib.md5(linePatternName.encode()).hexdigest()
        
        if rotation > 0:
            linePatternName = linePatternName \
                + '_R' + str(rotation)

        dstPath = TEMP_LOCATION + '/' + linePatternName + '.png'
        lineFillLayer.subSymbol().exportImage(dstPath, 'png', QSize(spacing, spacing))
        exporter.externalGraphics.append(dstPath)

        fillConfig = {
            'fill-pattern': linePatternName,
            'fill-opacity': 1
        }
        fillStyleLayer = self.exportFillLayerFormat(fillConfig)
        self.styles.append(fillStyleLayer)