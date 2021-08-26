from PyQt5.QtCore import QSize
from ..ekmap_common import *
from ..ekmap_converter import eKConverter
from ..qgslayer_parser.symbol_layer_factory import SymbolLayerFactory
import json, hashlib, os.path

class SymbologyParser():

    # This is abstract method
    def parse(self, renderer, exporter):
        raise NotImplementedError("Please Implement this method")

    def _wrapSymbolLayer(self, symbol, exporter):
        styleLayers = []
        for symbolLayer in symbol.symbolLayers():
            styleParser = SymbolLayerFactory.getLayerParser(symbolLayer, exporter)
            if styleParser is not None:
                styles = styleParser.parse()
                # Case POINT
                if symbolLayer.type() == 0:
                    key = json.dumps(styles)
                    key = hashlib.md5(key.encode()).hexdigest()
                    sizeUnit = eKConverter.convertRenderUnitValueToName(symbol.sizeUnit())
                    size = eKConverter.convertUnitToPixel(symbol.size(), sizeUnit)
                    exportImagePath = TEMP_LOCATION + '/' + key + '.png'
                    symbol.exportImage(exportImagePath, 'png', QSize(size, size))
                    if os.path.isfile(exportImagePath):
                        exporter.externalGraphics.append(exportImagePath)
                        styleLayers.append({
                            'type': 'symbol',
                            'layout': {
                                'icon-image': key
                            }
                        })
                # Case LINE or POLYGON
                else:
                    styleLayers.extend(styleParser.parse())

        return styleLayers