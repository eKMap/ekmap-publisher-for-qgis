from .symbology_parser import SymbologyParser

class SingleSymbolParser(SymbologyParser):

    def parse(self, singleSymbolRenderer, exporter):
        symbol = singleSymbolRenderer.symbol()
        return self._wrapSymbolLayer(symbol, exporter)