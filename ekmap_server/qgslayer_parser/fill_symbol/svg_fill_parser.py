from .fill_layer_parser import FillLayerParser
from ..symbol_layer_factory import *
from ...ekmap_converter import eKConverter
from ...ekmap_common import *

import hashlib, shutil

class SVGFillParser(FillLayerParser):
    
    def __init__(self, svgFillSymbolLayer, exporter):
        super().__init__(svgFillSymbolLayer)

        fillColor = svgFillSymbolLayer.color().name()
        rotation = int(svgFillSymbolLayer.angle())

        patternWidth = svgFillSymbolLayer.patternWidth()
        patternWidthUnit = svgFillSymbolLayer.patternWidthUnit()
        patternWidth = int(eKConverter.convertUnitToPixel(patternWidth, patternWidthUnit))

        svgPath = svgFillSymbolLayer.svgPath()
        svgName = hashlib.md5(svgPath.encode()).hexdigest()
        svgName =  svgName \
                + '_W' + patternWidth \
                + '_H' + patternWidth \
                + '_R' + rotation \
                + '_C' + fillColor \
                + '.svg'
        dstPath = TEMP_LOCATION + '/' + svgName
        shutil.copy2(svgPath, dstPath)
        exporter.externalGraphics.append(dstPath)

        fillConfig = {
            'fill-pattern': svgName,
            'fill-opacity': svgFillSymbolLayer.color().alpha() / 255
        }

        fillStyleLayer = self.exportFillLayerFormat(fillConfig)
        self.styles.append(fillStyleLayer)

        borderStyle = SymbolLayerFactory.getLayerParser(svgFillSymbolLayer.subSymbol(), exporter)
        self.styles.append(borderStyle.parse())