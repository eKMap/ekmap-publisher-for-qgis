from .line_layer_parser import LineLayerParser
from ...ekmap_converter import eKConverter

class SimpleLineParser(LineLayerParser):

    def __init__(self, simpleLineParser):
        super().__init__(simpleLineParser)

        lineConfig = self.initBaseLineConfig(simpleLineParser)

        # If using custom dash 
        # then replace default dash style
        isUseCustomDash = self.properties.get('use_custom_dash', '0')
        if isUseCustomDash == '1': # Use custom dash
            # Get custom dash array
            customDash = self.properties.get('customdash')
            # Get unit for convert
            customDashUnit = self.properties.get('customdash_unit')
            dasharray = []
            dashes = customDash.split(';')
            # For per value of dash array
            # Convert to pixel
            # and add to new dash array
            for dash in dashes:
                # Convert to pixel
                value = eKConverter.convertUnitToPixel(float(dash), customDashUnit)
                # Add to new dash array
                dasharray.append(float(value))
            # Replace default dash style
            lineConfig['line-dasharray'] = dasharray

        style = self.exportLineLayerFormat(lineConfig)
        self.styles.append(style)
        