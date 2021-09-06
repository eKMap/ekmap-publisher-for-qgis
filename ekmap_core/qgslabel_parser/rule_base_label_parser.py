from .label_parser import LabelParser
from ..filter_expression_parser.filter_parser import FilterParser
from ..ekmap_converter import eKConverter

class RuleBasedLabelParser(LabelParser):

    def __init__(self, labeling):
        super().__init__(labeling)

    def read(self):
        childrenStyle = self.labeling.rootRule().children()
        styleLabels = []
        for childStyle in childrenStyle:
            settings = childStyle.settings()
            styleLabel = self._readTextStyle(settings)

            # Set Filter
            filterExp = childStyle.filterExpression()
            filter = FilterParser.parse(filterExp)
            if filter is not None:
                styleLabel['filter'] = filter

            # Set min/max scale
            minScale = childStyle.minimumScale()
            if minScale > 0:
                minLevel = eKConverter.convertScaleToLevel(minScale)
                styleLabel['minzoom'] = minLevel
            maxScale = childStyle.maximumScale()
            if maxScale > 0:
                maxLevel = eKConverter.convertScaleToLevel(maxScale) - 1
                styleLabel['maxzoom'] = maxLevel

            styleLabels.append(styleLabel)
        return styleLabels