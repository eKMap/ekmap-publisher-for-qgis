from .fill_layer_parser import FillLayerParser
from ...ekmap_converter import eKConverter
from ...ekmap_common import *

import hashlib, shutil, importlib.util
from pathlib import Path 


class SVGFillParser(FillLayerParser):
    
    def __init__(self, svgFillSymbolLayer, exporter):
        super().__init__(svgFillSymbolLayer)

        fillColor = svgFillSymbolLayer.color().name()
        rotation = int(svgFillSymbolLayer.angle())

        patternWidth = svgFillSymbolLayer.patternWidth()
        patternWidthUnit = svgFillSymbolLayer.patternWidthUnit()
        patternWidth = int(eKConverter.convertUnitToPixel(patternWidth, patternWidthUnit))

        svgPath = svgFillSymbolLayer.svgFilePath()
        svgName = hashlib.md5(svgPath.encode()).hexdigest()
        svgName =  svgName \
                + '_W' + str(patternWidth) \
                + '_H' + str(patternWidth) \
                + '_C' + str(fillColor) 

        if rotation > 0:
            svgName = svgName \
                + '_R' + str(rotation)
        
        dstPath = TEMP_LOCATION + '/' + svgName + '.svg'
        shutil.copy2(svgPath, dstPath)
        exporter.externalGraphics.append(dstPath)

        fillConfig = {
            'fill-pattern': svgName,
            'fill-opacity': svgFillSymbolLayer.color().alpha() / 255
        }

        fillStyleLayer = self.exportFillLayerFormat(fillConfig)
        self.styles.append(fillStyleLayer)

        file = Path(__file__).resolve()
        parent = file.parent.parent
        spec = importlib.util.spec_from_file_location("eKMap-Publisher-For-QGIS.ekmap_server.qgslayer_parser.symbol_layer_factory", 
            str(parent) + "/symbol_layer_factory.py")
        
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        for subSymbol in svgFillSymbolLayer.subSymbol():
            borderStyle = foo.SymbolLayerFactory \
                .getLayerParser(subSymbol, exporter)
            self.styles.extend(borderStyle.parse())