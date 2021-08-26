from .rule_base_parser import RuleBasedParser
from .single_symbol_parser import SingleSymbolParser
from .categories_symbol_parser import CategoriesSymbolParser

class SymbologyFactory():

    def getSymbologyParser(renderer):
        if renderer is None:
            return None

        renderType = renderer.type()
        if renderType == 'RuleRenderer':
            return RuleBasedParser()
        elif renderType == 'singleSymbol':
            return SingleSymbolParser()
        elif renderType == 'categorizedSymbol':
            return CategoriesSymbolParser()
        else: # Not support
            return None