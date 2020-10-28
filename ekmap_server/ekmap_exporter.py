from qgis.core import QgsProject, Qgis, QgsRuleBasedRenderer, QgsVectorFileWriter, QgsMessageLog
from PyQt5.QtCore import QSize
from .ekmap_converter import eKConverter
from .ekmap_common import *
from .qgslayer_parser.symbol_layer_factory import SymbolLayerFactory

import os.path, json, uuid, urllib.parse, hashlib

class eKMapExporter:
    
    def __init__(self, iface, instance):
        eKConverter.IFACE = iface
        self.instance = instance
        self.sourcePaths = {}
        self.externalGraphics = []
        self.layerSorter = 0
        self.code = '';

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
        groupLayer["Type"] = "Group layer"
        return groupLayer

    def _wrapFeatureLayer(self, childLayer):
        mapLayer = childLayer.layer()
        layer = {}
        layer["Title"] = mapLayer.name()
        # layer["Code"] = self.code
        # layer["Description"] = mapLayer.abstract()

        if (mapLayer.providerType() == "ogr" 
            or mapLayer.providerType() == "delimitedtext"
            or mapLayer.providerType() == "spatialite"):
            if mapLayer.renderer() is None: # table
                # layer["Type"] = "Table"
                print('Temp comment')
            else:
                # layer["Type"] = "Feature layer"
                style = self._wrapStyle(mapLayer) # gọi trước để lấy giá trị GeoType
                # layer["GeoType"] = eKConverter.convertLayerToGeoType(self._geoType)
                # if style is not None:
                #     style = json.dumps(style)
                layer["Style"] = style
                styleLabel = self._wrapStyleLabel(mapLayer)
                # if styleLabel is not None:
                #     styleLabel = json.dumps(styleLabel)
                # layer["StyleLabel"] = styleLabel

                minLevel = eKConverter.convertScaleToLevel(mapLayer.minimumScale())
                maxLevel = eKConverter.convertScaleToLevel(mapLayer.maximumScale())
                if (maxLevel == 0):
                    maxLevel = 22
                    
                layer["MinLevel"] = minLevel
                layer["MaxLevel"] = maxLevel
            # layer["FieldInfo"] = self._wrapFieldInfos(mapLayer)
            layer["SourceWorkspace"] = self._wrapSourceWorkspace(mapLayer)
        else:
            layer["SourceWorkspace"] = self._wrapSourceWorkspaceProvider(mapLayer)
        # layer["DestWorkspace"] = None # ignore in this time
        # layer["Config"] = None # ignore in this time
        # layer["Filter"] = None # ignore in this time
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

    def _wrapSourceWorkspaceProvider(self, mapLayer):
        sourceWorkspace = {}
        params = eKMapCommonHelper.urlParamToMap(mapLayer.publicSource())

        if mapLayer.providerType() == 'wms':
            sourceWorkspace["ConnectString"] = urllib.parse.unquote(params["url"])
            sourceWorkspace["Provider"] = eKConverter.convertExtensionToName(params["type"])

        return sourceWorkspace

    def _wrapSourceWorkspace(self, mapLayer):
        sourceWorkspace = {}
        
        source = mapLayer.publicSource()
        basename = os.path.basename(source)
        baseSplit = basename.split(".")

        ext = baseSplit[-1].lower()
        provider = eKConverter.convertExtensionToName(baseSplit[-1])
        if provider is None:
            provider = 'SQLite'
            ext = 'sqlite'
            fileName = TEMP_LOCATION + '/' + mapLayer.name() + '.' + ext
            basename = mapLayer.name() + '.' + ext
            self.sourcePaths[mapLayer.id()] = fileName # Nếu còn trùng thì đổi self.code

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = provider
            options.fileEncoding = "UTF-8"
            QgsVectorFileWriter.writeAsVectorFormatV2(mapLayer, fileName, self.instance.transformContext(), options)
        else:
            self.sourcePaths[mapLayer.id()] = source # Nếu còn trùng thì đổi self.code

        sourceWorkspace["ConnectString"] = mapLayer.id() + "\\" + basename # Nếu còn trùng thì đổi self.code
        sourceWorkspace["Provider"] = provider # tách extension
        # sourceWorkspace["TableName"] = None 

        # sourceWorkspace["Projection"] = "4326" # tạm fix cứng
        return sourceWorkspace

    def _wrapStyleLabel(self, mapLayer):
        if mapLayer.labeling() is None:
            return None
        elif mapLayer.labeling().type() != 'simple':
            return DEFAULT_STYLE_LABEL
        return self._wrapSimpleLabelStyle(mapLayer.labeling().settings())

    def _wrapSimpleLabelStyle(self, settings):
        labelStyle = {}
        labelStyle["field"] = settings.fieldName
        labelStyle["labelXOffset"] = int(settings.xOffset)
        labelStyle["labelYOffset"] = int(settings.yOffset)
        labelStyle["fontName"] = settings.format().font().family()
        labelStyle["fontSize"] = int(settings.format().size())
        labelStyle["fontColor"] = settings.format().color().name()
        labelStyle["fontStyle"] = settings.format().namedStyle()
        labelStyle["strokeColor"] = settings.format().buffer().color().name()
        labelStyle["strokeWidth"] = int(settings.format().buffer().size())
        labelStyle["opacity"] = settings.format().opacity()

        minLevel = 0
        maxLevel = 22
        if settings.scaleVisibility:
            minLevel = eKConverter.convertScaleToLevel(settings.minimumScale)
            if (settings.maximumScale != 0):
                maxLevel = eKConverter.convertScaleToLevel(settings.maximumScale)

        labelStyle["level"] = str(minLevel) + "," + str(maxLevel)
        
        return labelStyle

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
        # style = {}
        # rules = []
        # for childRule in ruleBasedRenderer.rootRule().children():
        #     rule = {}

        #     # Get title
        #     rule["title"] = childRule.label()

        #     # Get symbol
        #     rule = self._wrapSymbolLayers(childRule.symbol(), rule)

        #     # Get filter
        #     if childRule.filter() is not None:
        #         expression = childRule.filter().expression()
        #         rule["filter"] = self._wrapFilterExpression(expression)
        #         rules.append(rule)
        #     else:
        #         style["defaultStyle"] = rule

        # style["rules"] = rules
        # return style
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
        # style = {}
        # rules = []
        # selectedProperty = renderer.classAttribute()
        # for category in renderer.categories():
        #     rule = {}
        #     # Get symbol
        #     rule = self._wrapSymbolLayers(category.symbol())
        #     # Get filter
        #     if category.label().strip():
        #         rule["title"] = category.label()
        #         rule["filter"] = {
        #             "property": selectedProperty,
        #             "type": "=",
        #             "value": category.value()
        #         }
        #         rules.append(rule)
        #     else:
        #         style["defaultStyle"] = rule

        # style["rules"] = rules
        # return style
        styles = []
        selectedProperty = renderer.classAttribute()
        for category in renderer.categories():
            styleLayers = self._wrapSymbolLayers(category.symbol())
            # Get filter
            if category.label().strip():
                for styleLayer in styleLayers:
                    styleLayer['filter'] = [
                        "==",
                        [
                            "get",
                            selectedProperty,
                        ],
                        category.value()
                    ]

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
            styleLayer = SymbolLayerFactory.getLayerParser(symbolLayer)
            if styleLayer is not None:
                styles = styleLayer.parse()
                
                # Comment the old version
                # styleLayers.extend(styleLayer.parse())

                # This is updated version
                # Case Marker, export image and generate symbol layer style
                # instead of eKMarker layer style
                # the eKMarker layer style used for generate style key to identify image
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
                            'type': 'ekmarker',
                            'layout': {
                                'marker-name': 'raster-image',
                                'marker-image': 'D:/exo/Test2/_externalGraphic/' + key + '.png'
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