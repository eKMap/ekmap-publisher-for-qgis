from .simple_label_parser import SimpleLabelParser
from .rule_base_label_parser import RuleBasedLabelParser

class LabelFactory:

    def getLabelParser(mapLayer):
        labeling = mapLayer.labeling()
        if labeling is None:
            return None
        elif labeling.type() == 'rule-based':
            return RuleBasedLabelParser(labeling)
        else: # 'simple'
            return SimpleLabelParser(labeling)