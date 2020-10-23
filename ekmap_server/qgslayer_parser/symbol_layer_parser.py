class SymbolLayerParser:

    DEFAULT_MARKER_CONFIG = {
        'marker-name': 'circle',
        'marker-width': 1, # pixel
        'marker-height': 1, # pixel
        'marker-image': None,
        'marker-color': '#000000',
    }
    
    DEFAULT_LINE_CONFIG = {
        'line-cap': 'square',
        'line-join': 'bevel',
        'line-color': '#000000',
        'line-dasharray': None,
        'line-opacity': 1, # from 0 ~ 1
        'line-width': 1, # pixel
    }

    DEFAULT_FILL_CONFIG = {
        'fill-color': '#000000',
        'fill-opacity': 1 # from 0 ~ 1
    }

    def __init__(self, symbolLayer):
        self.styles = []
        self.properties = symbolLayer.properties()

    def parse(self):
        return self.styles
    
    # Using eKMarker - user definition format based on Mapbox
    # because Mapbox style specifiation not support other format
    # Mapbox using image instead
    # in this case, eKMapServer would render image based on definition format
    def exporteKMarkerLayerFormat(self, shapeConfig):
        return {
            'type': 'ekmarker',
            'paint': {
                'marker-color': shapeConfig['marker-color'],
            },
            'layout': {
                'marker-name': shapeConfig['marker-name'],
                'marker-width': shapeConfig['marker-width'],
                'marker-height': shapeConfig['marker-height'],
                'marker-image': shapeConfig['marker-image'],
            }
        }


    def exportLineLayerFormat(self, lineConfig):
        return {
            'type': 'line',
            'paint': {
                'line-color': lineConfig['line-color'],
                'line-dasharray': lineConfig['line-dasharray'],
                'line-width': lineConfig['line-width'],
                'line-opacity': lineConfig['line-opacity'],
            },
            'layout': {
                'line-cap': lineConfig['line-cap'],
                'line-join': lineConfig['line-join'],
            },
        }

    def exportFillLayerFormat(self, fillConfig):
        return {
            'type': 'fill',
            'paint': {
                'fill-color': fillConfig['fill-color'],
                'fill-opacity': fillConfig['fill-opacity'],
            }
        }