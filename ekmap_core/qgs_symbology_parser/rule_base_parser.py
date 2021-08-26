from .symbology_parser import SymbologyParser
from ..filter_expression_parser.filter_parser import FilterParser

class RuleBasedParser(SymbologyParser):

    def parse(self, ruleBasedRenderer, exporter):
        styles = []
        for childRule in ruleBasedRenderer.rootRule().children():
            symbol = childRule.symbol()
            styleLayers = self._wrapSymbolLayer(symbol, exporter)

            # Set filter
            if childRule.filter() is not None:
                expression = childRule.filter().expression()
                for styleLayer in styleLayers:
                    styleLayer['filter'] = FilterParser.parse(expression)

            # Set active
            isVisible = 'visible'
            if not childRule.active():
                isVisible = 'none'
            for styleLayer in styleLayers:
                styleLayer['layout']['visibility'] = isVisible

            styles.extend(styleLayers) 
        return styles