from qgis.core import QgsApplication
from PyQt5.QtCore import QSize
from .ekmap_converter import eKConverter
from .ekmap_logger import eKLogger
from .ekmap_common import *
from .qgssource_parser.datasource_parser import DataSourceParser
from .qgslayer_parser.symbol_layer_factory import SymbolLayerFactory
from .qgslabel_parser.simple_label_parser import SimpleLabelParser

import os.path, json, uuid, hashlib

class eKMapExporter:
    
    def __init__(self, iface, instance):
        eKConverter.IFACE = iface
        self.instance = instance
        self.sourceParser = DataSourceParser()
        self.externalGraphics = []
        self.layerSorter = 0
        self.code = ''
        self.ogr2ogr = QgsApplication.prefixPath().rstrip('apps/qgis') + '/bin/ogr2ogr.exe'

    def exportMapInfo(self):
        mapInfo = {}
        mapInfo["Title"] = self.instance.baseName()
        mapInfo["Description"] = None # không tìm thấy
        mapInfo["CurrentView"] = self._wrapCurrentView()
        mapInfo["MaxExtent"] = self._wrapExtent(eKConverter.IFACE.mapCanvas().fullExtent())
        mapInfo["RestrictExtent"] = self._wrapExtent(eKConverter.IFACE.mapCanvas().fullExtent())

        mapScales = self.instance.viewSettings().mapScales()
        minLevel = 0 # mặc định
        maxLevel = 22 # mặc định
        if len(mapScales) > 0 :
            minLevel = eKConverter.convertScaleToLevel(mapScales[0])
            maxLevel = eKConverter.convertScaleToLevel(mapScales[len(mapScales) - 1])
        mapInfo["MinLevel"] = minLevel 
        mapInfo["MaxLevel"] = maxLevel 
        mapInfo["Config"] = None # chưa support
        mapInfo["Source"] = None # chưa support

        mapInfo["Layers"] = self._wrapLayers(self.instance.layerTreeRoot(), None)
        
        return mapInfo

    def _wrapCurrentView(self):
        currentView = {}
        currentView["x"] = eKConverter.IFACE.mapCanvas().center().x()
        currentView["y"] = eKConverter.IFACE.mapCanvas().center().y()
        currentView["level"] = eKConverter.convertScaleToLevel(eKConverter.IFACE.mapCanvas().scale())
        return currentView

    def _wrapExtent(self, inputExtent):
        extent = {}
        extent["xmin"] = inputExtent.xMinimum()
        extent["xmax"] = inputExtent.xMaximum()
        extent["ymin"] = inputExtent.yMinimum()
        extent["ymax"] = inputExtent.yMaximum()
        return extent

    def _wrapLayers(self, root, parentCode):
        layers = []
        for childLayer in root.children():
            layer = {}
            self.code = str(uuid.uuid4())
            if childLayer.nodeType() == 1: # feature layer
                # Nếu không phải vector layer thì bỏ qua
                #if childLayer.layer().type().value != 0:
                #    continue
                layer = self._wrapFeatureLayer(childLayer)
            else: # group layer
                layer = self._wrapGroupLayer(childLayer)

            self.layerSorter = self.layerSorter + 1
            layer["Sorter"] = self.layerSorter

            if parentCode is not None:
                layer["ParentCode"] = parentCode
            layers.append(layer)
            if len(childLayer.children()) > 0:
                layers.extend(self._wrapLayers(childLayer, layer["Code"]))
        return layers

    def _wrapGroupLayer(self, node):
        groupLayer = {}
        groupLayer["Title"] = node.name()
        groupLayer["Code"] = self.code
        groupLayer["Type"] = "Group Layer"
        return groupLayer

    def _wrapFeatureLayer(self, childLayer):
        mapLayer = childLayer.layer()
        layer = {}
        layer["Title"] = mapLayer.name()
        layer["Code"] = self.code
        layer["Description"] = mapLayer.abstract()
        providerType = mapLayer.providerType()
        sourceString = mapLayer.source()
        if (providerType == "ogr" 
            or providerType == "delimitedtext" # CSV
            or providerType == "spatialite"): # SQLite
            if mapLayer.renderer() is None: # table
                layer["Type"] = "Table"
            else:
                layer["Type"] = "Feature Layer"
                style = self._wrapStyle(mapLayer) # gọi trước để lấy giá trị GeoType
                styleLabel = self._wrapStyleLabel(mapLayer)
                if styleLabel is not None:
                    # style.append(styleLabel)
                    styleLabel = json.dumps(styleLabel)
                    layer["StyleLabel"] = styleLabel
                layer["GeoType"] = eKConverter.convertLayerToGeoType(self._geoType)
                if style is not None:
                    style = json.dumps(style)
                    layer["Style"] = style

                minLevel = 0 
                maxLevel = 22
                if mapLayer.hasScaleBasedVisibility():
                    minLevel = eKConverter.convertScaleToLevel(mapLayer.minimumScale())
                    maxLevel = eKConverter.convertScaleToLevel(mapLayer.maximumScale())
                if (maxLevel == 0):
                    maxLevel = 22
                    
                layer["MinLevel"] = minLevel
                layer["MaxLevel"] = maxLevel
            layer["FieldInfo"] = self._wrapFieldInfos(mapLayer)
            # layer["SourceWorkspace"] = self._wrapSourceWorkspace(mapLayer)
        layer["SourceWorkspace"] = self.sourceParser.parse(providerType, sourceString)
        # layer["DestWorkspace"] = None # ignore in this time
        # layer["Config"] = None # ignore in this time
        layer["Filter"] = self.sourceParser.currentSourceFilter
        layer["Visible"] = childLayer.isVisible()
        # layer["BaseLayer"] = False # not support
        
        return layer

    def _wrapFieldInfos(self, mapLayer):
        fieldInfos = []
        i = 1
        for field in mapLayer.fields():
            fieldInfos.append(self._wrapFieldInfo(field, i))
            i = i + 1
        return fieldInfos

    def _wrapFieldInfo(self, field, increment):
        fieldInfo = {}
        fieldInfo["TableName"] = None # ignore in this time
        fieldInfo["FieldName"] = field.name()
        fieldInfo["FieldSource"] = field.name() # lấy giống field name
        fieldInfo["DisplayName"] = field.displayName()
        fieldInfo["DataType"] = eKConverter.convertDataType(field.typeName())
        if field.length() == 1:
            fieldInfo["Length"] = 10
        else:
            fieldInfo["Length"] = field.length()
        fieldInfo["AllowNull"] = True # tạm fix cứng
        fieldInfo["ViewType"] = "lineedit"
        fieldInfo["Sorter"] = increment # tăng dần
        return fieldInfo

    def _wrapStyleLabel(self, mapLayer):
        # if mapLayer.labeling() is None:
        #     return None
        # elif mapLayer.labeling().type() != 'simple':
        #     return DEFAULT_STYLE_LABEL
        return self._wrapSimpleLabelStyle(mapLayer)

    def _wrapSimpleLabelStyle(self, mapLayer):
        labelLayer = SimpleLabelParser(mapLayer)
        return labelLayer.read()

    def _wrapStyle(self, mapLayer):
        if mapLayer.renderer() is None: # table
            return None
        if mapLayer.renderer().type() == 'RuleRenderer':
            return self._wrapRuleBasedStyle(mapLayer.renderer())
        if mapLayer.renderer().type() == 'singleSymbol':
            return self._wrapSingleSymbolStyle(mapLayer.renderer())
        if mapLayer.renderer().type() == 'categorizedSymbol':
            return self._wrapCategoriesSymbolStyle(mapLayer.renderer())
        return eKMapCommonHelper.getDefaultStyleBaseOnGeoType(mapLayer.type().value)

    def _wrapSingleSymbolStyle(self, singleSymbolRenderer):
        # self._geoType = singleSymbolRenderer.symbol().type()
        return self._wrapSymbolLayers(singleSymbolRenderer.symbol())
        
    def _wrapRuleBasedStyle(self, ruleBasedRenderer):
        styles = []
        for childRule in ruleBasedRenderer.rootRule().children():
            styleLayers = self._wrapSymbolLayers(childRule.symbol())

            # Set filter
            if childRule.filter() is not None:
                expression = childRule.filter().expression()
                for styleLayer in styleLayers:
                    styleLayer['filter'] = self._wrapFilterExpression(expression)

            # Set active
            isVisible = 'visible'
            if not childRule.active():
                isVisible = 'none'
            for styleLayer in styleLayers:
                styleLayer['layout']['visibility'] = isVisible

            styles.extend(styleLayers) 
        return styles

    def _wrapCategoriesSymbolStyle(self, renderer):
        styles = []
        selectedProperty = renderer.classAttribute()

        # Find else conditions:
        categoryDumps = renderer.dump().split('\n')
        otherValues = []
        for categoryDump in categoryDumps:
            lineSplit = categoryDump.split('::')
            if len(lineSplit) > 1 and lineSplit[0] != '':
                otherValues.append(lineSplit[0])
        elseFilter = [
            "!",
            [
                "in",
                [
                    "get",
                    renderer.classAttribute()
                ],
                [
                    "literal",
                    otherValues
                ]
            ]
        ]

        for category in renderer.categories():
            styleLayers = self._wrapSymbolLayers(category.symbol())
            # Get filter
            dummyInfos = category.dump().split('::')
            currentFilter = elseFilter
            if dummyInfos[0] != '':
                currentFilter = [
                    "==",
                    [
                        "get",
                        selectedProperty,
                    ],
                    category.value()
                ]
            for styleLayer in styleLayers:
                styleLayer['filter'] = currentFilter

            # Set active
            isVisible = 'visible'
            if not category.renderState():
                isVisible = 'none'
            for styleLayer in styleLayers:
                styleLayer['layout']['visibility'] = isVisible

            styles.extend(styleLayers) 
        return styles

    def _wrapSymbolLayers(self, symbol):
        self._geoType = symbol.type()
        styleLayers = []
        for symbolLayer in symbol.symbolLayers():
            styleLayer = SymbolLayerFactory.getLayerParser(symbolLayer, self)
            if styleLayer is not None:
                styles = styleLayer.parse()
                if symbolLayer.type() == 0:
                    key = json.dumps(styles)
                    key = hashlib.md5(key.encode()).hexdigest()
                    sizeUnit = eKConverter.convertRenderUnitValueToName(symbol.sizeUnit())
                    size = eKConverter.convertUnitToPixel(symbol.size(), sizeUnit)
                    exportImagePath = TEMP_LOCATION + '/' + key + '.png'
                    symbol.exportImage(exportImagePath, 'png', QSize(size, size))
                    if os.path.isfile(exportImagePath):
                        self.externalGraphics.append(exportImagePath)
                        styleLayers.append({
                            'type': 'symbol',
                            'layout': {
                                'icon-image': key
                            }
                        })
                    #else:
                    #    QgsMessageLog.logMessage(json.dumps(styles) + " is exported fail!", 'eKMapServer Publisher', level=Qgis.Info)
                # Case Line and Polygon
                else:
                    styleLayers.extend(styleLayer.parse())

        return styleLayers

    def _wrapFilterExpression(self, filterExpression):
        filterObj = {}
        # Filter có dạng "{Tên trường} {Filter} {Giá trị}"
        # Tạm thời hỗ trợ type Equal
        filterType = "="
        filterExps = filterExpression.split(filterType) # filterExpression.split(" ")
        if len(filterExps) != 2:
            return None
        filterObj["property"] = filterExps.pop(0).replace("\"","")
        filterObj["type"] = filterType #filterExps.pop(0)

        # Giá trị có thể có khoảng trắng ở giữa
        # Bỏ đi dấu nháy ở đầu
        filterObj["value"] = " ".join(filterExps).replace("'","")
        return [
            "==",
            [
                "get",
                filterObj["property"]
            ],
            filterObj["value"]
        ]