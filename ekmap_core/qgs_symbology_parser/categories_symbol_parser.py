from .symbology_parser import SymbologyParser

class CategoriesSymbolParser(SymbologyParser):

    def parse(self, renderer, exporter):
        styles = []
        selectedProperty = renderer.classAttribute()

        # Find else conditions:
        otherValues = self.__getDetailOtherValues(renderer.dump())
        elseFilter = self.__buildElseFilter(selectedProperty, otherValues)

        # pointDict = {}
        pointTuples =  []
        pointFallback = ''
        for category in renderer.categories():
            # Check active
            if not category.renderState():
                continue

            symbol = category.symbol()
            styleLayers = self._wrapSymbolLayer(symbol, exporter)
            # Get filter
            currentFilter = self.__getFilter(selectedProperty, category)
            
            # for styleLayer in styleLayers:
            #     styleLayer['layout']['visibility'] = 'visible'

            if symbol.type() != 0: # Is LINE or POLYGON
                if currentFilter is None:
                    currentFilter = elseFilter
                # Apply filter for layers
                for styleLayer in styleLayers:
                    styleLayer['filter'] = currentFilter
                styles.extend(styleLayers) 
            else: # POINT
                key = self.__extractIconKey(styleLayers)
                if currentFilter is None:
                    pointFallback = key
                else:
                    pointTuple = (currentFilter, key)
                    pointTuples.append(pointTuple)
                    # pointDict[currentFilter] = key
        pointStyle = self.__parsePoint(pointTuples, pointFallback)
        if pointStyle is not None:
            styles.append(pointStyle)
        return styles

    def __getDetailOtherValues(self, dump):
        categoryDumps = dump.split('\n')
        otherValues = []
        for categoryDump in categoryDumps:
            lineSplit = categoryDump.split('::')
            if len(lineSplit) > 1 and lineSplit[0] != '':
                otherValues.append(lineSplit[0])
        return otherValues

    def __buildElseFilter(self, selectedProperty, otherValues):
        return [
            "!",
            [
                "in",
                [
                    "get",
                    selectedProperty
                ],
                [
                    "literal",
                    otherValues
                ]
            ]
        ]

    def __parseFilter(self, selectedProperty, value):
        return [
                "==",
                [
                    "get",
                    selectedProperty,
                ],
                value
            ]

    def __getFilter(self, selectedProperty, category):
        dummyInfos = category.dump().split('::')
        if dummyInfos[0] != '':
            return self.__parseFilter(selectedProperty, category.value())
        else:
            return None

    def __extractIconKey(self, styleLayers):
        # In case Symbol Icon, there is only one styleLayer
        if len(styleLayers) > 0:
            styleLayer = styleLayers[0]
            key = styleLayer['layout']['icon-image']
            return key
        else:
            return None

    def __parsePoint(self, pointTuples, pointDefault):
        if len(pointTuples) == 0:
            return None
        else:
            case = []
            case.append('case')
            for pointTuple in pointTuples:
                for pTuple in pointTuple:
                    case.append(pTuple)
                # case.append(key) # condition
                # case.append(pointDict[key]) # image name
            case.append(pointDefault)
            return {
                'type': 'symbol',
                'layout': {
                    'icon-image': case
                }
            }