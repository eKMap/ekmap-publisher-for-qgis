from .label_parser import LabelParser

class SimpleLabelParser(LabelParser):

    def __init__(self, labeling):
        super().__init__(labeling)
        
    def read(self):
        settings = self.labeling.settings()
        # styleLayer = self.readZoomLevel()
        styleLabel = self._readTextStyle(settings)
        # self.readBackground()
        # self.readPlacement()

        return [styleLabel]