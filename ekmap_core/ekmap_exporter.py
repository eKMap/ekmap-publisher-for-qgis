from qgis.core import QgsApplication, QgsMessageLog
from PyQt5.QtCore import QSize
from .ekmap_converter import eKConverter
from .ekmap_logger import eKLogger
from .ekmap_common import *
from .qgssource_parser.datasource_parser import DataSourceParser
from .qgslayer_parser.symbol_layer_factory import SymbolLayerFactory
from .qgslabel_parser.label_factory import LabelFactory
from .qgs_symbology_parser.symbology_factory import SymbologyFactory

import json, uuid

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
        QgsMessageLog.logMessage('Start Layer')
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
            QgsMessageLog.logMessage('Layer ' + str(childLayer.name()))
            layer = {}
            if childLayer.nodeType() == 1: # feature layer
                # Nếu không phải vector layer thì bỏ qua
                #if childLayer.layer().type().value != 0:
                #    continue
                self.code = childLayer.layer().id()
                layer = self._wrapFeatureLayer(childLayer)
            else: # group layer
                self.code = str(uuid.uuid4())
                layer = self._wrapGroupLayer(childLayer)

            # layer["Id"] = self.layerSorter
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
            or providerType == "mssql"
            or providerType == "spatialite"): # SQLite
            if mapLayer.renderer() is None: # table
                layer["Type"] = "Table"
            else:
                geoType = mapLayer.geometryType()
                layer["GeoType"] = eKConverter.convertLayerToGeoType(geoType)
                layer["Type"] = "Feature Layer"
                style = self._wrapStyle(mapLayer)
                styleLabel = self._wrapStyleLabel(mapLayer)
                if styleLabel is not None:
                    # style.append(styleLabel)
                    styleLabel = json.dumps(styleLabel)
                    layer["StyleLabel"] = styleLabel
                if style is not None:
                    style = json.dumps(style)
                    layer["Style"] = style

                minLevel = 0 
                maxLevel = 22
                if mapLayer.hasScaleBasedVisibility():
                    minLevel = eKConverter.convertScaleToLevel(mapLayer.minimumScale())
                    maxLevel = eKConverter.convertScaleToLevel(mapLayer.maximumScale()) - 1
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
        # return self._wrapSimpleLabelStyle(mapLayer)
        labelParser = LabelFactory.getLabelParser(mapLayer)
        if labelParser is None:
            return None
        else:
            return labelParser.read()

    # def _wrapSimpleLabelStyle(self, mapLayer):
    #     labelLayer = SimpleLabelParser(mapLayer)
    #     return labelLayer.read()

    def _wrapStyle(self, mapLayer):
        renderer = mapLayer.renderer()
        symbologyParser = SymbologyFactory.getSymbologyParser(renderer)
        if symbologyParser is None:
            return None
        else:
            return symbologyParser.parse(renderer, self)