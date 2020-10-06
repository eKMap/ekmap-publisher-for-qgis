from qgis.core import QgsProject, Qgis, QgsRuleBasedRenderer, QgsVectorFileWriter, QgsMessageLog
from .ekmap_converter import *
from .ekmap_common import *

import os.path, json, uuid, urllib.parse

class EKMapExporter:
    def __init__(self, iface, instance):
        self.iface = iface
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
        mapInfo["MaxExtent"] = self._wrapExtent(self.iface.mapCanvas().fullExtent())
        mapInfo["RestrictExtent"] = self._wrapExtent(self.iface.mapCanvas().fullExtent())

        mapScales = self.instance.viewSettings().mapScales()
        minLevel = 0 # mặc định
        maxLevel = 22 # mặc định
        if len(mapScales) > 0 :
            minLevel = convertScaleToLevel(self.iface, mapScales[0])
            maxLevel = convertScaleToLevel(self.iface, mapScales[len(mapScales) - 1])
        mapInfo["MinLevel"] = minLevel 
        mapInfo["MaxLevel"] = maxLevel 
        mapInfo["Config"] = None # chưa support
        mapInfo["Source"] = None # chưa support

        mapInfo["Layers"] = self._wrapLayers(self.instance.layerTreeRoot(), None)
        return mapInfo

    def _wrapCurrentView(self):
        currentView = {}
        currentView["x"] = self.iface.mapCanvas().center().x()
        currentView["y"] = self.iface.mapCanvas().center().y()
        currentView["level"] = convertScaleToLevel(self.iface, self.iface.mapCanvas().scale())
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
        layer["Code"] = self.code
        layer["Description"] = mapLayer.abstract()

        if (mapLayer.providerType() == "ogr" 
            or mapLayer.providerType() == "delimitedtext"
            or mapLayer.providerType() == "spatialite"):
            if mapLayer.renderer() is None: # table
                layer["Type"] = "Table"
            else:
                layer["Type"] = "Feature layer"
                style = self._wrapStyle(mapLayer) # gọi trước để lấy giá trị GeoType
                layer["GeoType"] = convertLayerToGeoType(self._geoType)
                if style is not None:
                    style = json.dumps(style)
                layer["Style"] = style
                styleLabel = self._wrapStyleLabel(mapLayer)
                if styleLabel is not None:
                    styleLabel = json.dumps(styleLabel)
                layer["StyleLabel"] = styleLabel

                minLevel = convertScaleToLevel(self.iface, mapLayer.minimumScale())
                maxLevel = convertScaleToLevel(self.iface, mapLayer.maximumScale())
                if (maxLevel == 0):
                    maxLevel = 22
                    
                layer["MinLevel"] = minLevel
                layer["MaxLevel"] = maxLevel
            layer["FieldInfo"] = self._wrapFieldInfos(mapLayer)
            layer["SourceWorkspace"] = self._wrapSourceWorkspace(mapLayer)
        else:
            layer["SourceWorkspace"] = self._wrapSourceWorkspaceProvider(mapLayer)
        layer["DestWorkspace"] = None # chưa cần quan tâm
        layer["Config"] = None # chưa cần quan tâm
        layer["Filter"] = None # chưa cần quan tâm
        layer["Visible"] = childLayer.isVisible()
        layer["BaseLayer"] = False # chưa support
        
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
        fieldInfo["TableName"] = None # chưa cần quan tâm
        fieldInfo["FieldName"] = field.name()
        fieldInfo["FieldSource"] = field.name() # lấy giống field name
        fieldInfo["DisplayName"] = field.displayName()
        fieldInfo["DataType"] = convertDataType(field.typeName())
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
        params = EKMapCommonHelper.urlParamToMap(mapLayer.publicSource())

        if mapLayer.providerType() == 'wms':
            sourceWorkspace["ConnectString"] = urllib.parse.unquote(params["url"])
            sourceWorkspace["Provider"] = convertExtensionToName(params["type"])

        #elif mapLayer.providerType() == 'wms':
        #    sourceWorkspace["ConnectString"] = params["url"]
        #    sourceWorkspace["Provider"] = params["type"]

        return sourceWorkspace

    def _wrapSourceWorkspace(self, mapLayer):
        sourceWorkspace = {}
        
        source = mapLayer.publicSource()
        basename = os.path.basename(source)
        baseSplit = basename.split(".")

        ext = baseSplit[-1].lower()
        provider = convertExtensionToName(baseSplit[-1])
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
        sourceWorkspace["TableName"] = None 

        sourceWorkspace["Projection"] = "4326" # tạm fix cứng
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
            minLevel = convertScaleToLevel(self.iface, settings.minimumScale)
            if (settings.maximumScale != 0):
                maxLevel = convertScaleToLevel(self.iface, settings.maximumScale)

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
        return EKMapCommonHelper.getDefaultStyleBaseOnGeoType(mapLayer.type().value)

    def _wrapSingleSymbolStyle(self, singleSymbolRenderer):
        self._geoType = singleSymbolRenderer.symbol().type()

        return {
            "rules": [],
            "defaultStyle": self._wrapSymbolLayers(singleSymbolRenderer.symbol(),{})
        }
        
    def _wrapRuleBasedStyle(self, ruleBasedRenderer):
        style = {}
        rules = []
        for childRule in ruleBasedRenderer.rootRule().children():
            rule = {}

            # Get title
            rule["title"] = childRule.label()

            # Get symbol
            rule = self._wrapSymbolLayers(childRule.symbol(), rule)

            # Get filter
            if childRule.filter() is not None:
                expression = childRule.filter().expression()
                rule["filter"] = self._wrapFilterExpression(expression)
                rules.append(rule)
            else:
                style["defaultStyle"] = rule

        style["rules"] = rules
        return style

    def _wrapCategoriesSymbolStyle(self, renderer):
        style = {}
        rules = []
        selectedProperty = renderer.classAttribute()
        for category in renderer.categories():
            rule = {}
            # Get symbol
            rule = self._wrapSymbolLayers(category.symbol(), rule)
            # Get filter
            if category.label().strip():
                rule["title"] = category.label()
                rule["filter"] = {
                    "property": selectedProperty,
                    "type": "=",
                    "value": category.value()
                }
                rules.append(rule)
            else:
                style["defaultStyle"] = rule

        style["rules"] = rules
        return style

    def _wrapSymbolLayers(self, symbol, rule):
        self._geoType = symbol.type()

        for symbolLayer in symbol.symbolLayers():
            properties = symbolLayer.properties()

            outputDpi = self.iface.mapCanvas().mapSettings().outputDpi()
            if self._geoType == 0: # áp dụng riêng với POINT
                name = str(properties.get("name"))
                if name is None:
                    rule["graphicName"] = ""
                
                # if name is path
                elif os.path.isfile(name):
                    self.externalGraphics.append(name)
                    external = os.path.basename(name)
                    rule["externalGraphic"] = "_externalGraphic" + "\\" +external
                # else name is not path
                else:
                    rule["graphicName"] = convertGraphicNameToVieType(name)
                
                if properties.get("imageFile") is not None:
                    imageFile = properties.get("imageFile")
                    self.externalGraphics.append(imageFile)
                    external = os.path.basename(imageFile)
                    rule["externalGraphic"] = "_externalGraphic" + "\\" + external

                size = properties.get("size")
                if size is not None:
                    sizeUnit = properties.get("size_unit")
                    rule["graphicHeight"] = int(convertUnitToPixel(outputDpi, size, sizeUnit))
                    rule["graphicWidth"] = int(convertUnitToPixel(outputDpi, size, sizeUnit))
                
                offset = properties.get("offset")
                if offset is not None:
                    offsets = offset.split(",")
                    if len(offsets) == 2:
                        offsetUnit = properties.get("offset_unit")
                        rule["graphicXOffset"] = int(convertUnitToPixel(outputDpi, offsets[0], offsetUnit))
                        rule["graphicYOffset"] = int(convertUnitToPixel(outputDpi, offsets[1], offsetUnit))
            
            if self._geoType == 1: # Là line
                # Line của QGIS không có stroke
                # Lấy fill color của QGIS thay stroke color của EKMap
                outlineWidth = properties.get("line_width")
                if outlineWidth is not None:
                    outlineWidthUnit = properties.get("line_width_unit")
                    rule["strokeWidth"] = int(convertUnitToPixel(outputDpi, outlineWidth, outlineWidthUnit))
                rule["strokeColor"] = symbolLayer.color().name()
                rule["strokeOpacity"] = symbolLayer.color().alpha() / 255
                rule["strokeDashstyle"] = convertStrokeTypeToVieType(properties.get("line_style"))
            else: # Là point hoặc polygon
                rule["fillColor"] = symbolLayer.color().name()
                rule["fillOpacity"] = symbolLayer.color().alpha() / 255 

                outlineWidth = properties.get("outline_width")
                if outlineWidth is not None:
                    outlineWidthUnit = properties.get("outline_width_unit")
                    rule["strokeWidth"] = int(convertUnitToPixel(outputDpi, outlineWidth, outlineWidthUnit))
                rule["strokeColor"] = symbolLayer.strokeColor().name()
                rule["strokeOpacity"] = symbolLayer.strokeColor().alpha() / 255
                rule["strokeDashstyle"] = convertStrokeTypeToVieType(properties.get("outline_style"))
        return rule

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
        return filterObj