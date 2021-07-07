import os, hashlib, urllib, re
from ..ekmap_common import *
from ..ekmap_converter import eKConverter
from ..ekmap_logger import eKLogger
from .filesource_helper import FileSourceHelper

class DataSourceParser():

    def __init__(self):
        self.sourcePaths = {}
        self.currentSourceFilter = ''

    # Support gdal, ogr, wms
    # Upcoming delimitedtext, mssql
    def parse(self, providerType ,sourceString):
        self.currentSourceFilter = ''
        if providerType == 'gdal':
            return self.__parseGdal(sourceString)
        elif providerType == 'wms':
            return self.__parseWms(sourceString)
        elif providerType == 'ogr':
            return self.__parseOgr(sourceString)
        elif providerType == 'mssql':
            return self.__parseMssql(sourceString)
        else:
            return None

    # For case ZXY
    # Missing case OGC WMS
    def __parseWms(self, sourceString):
        sourceWorkspace = {}
        params = eKMapCommonHelper.urlParamToMap(sourceString)
        sourceWorkspace["ConnectString"] = urllib.parse.unquote(params["url"])
        if 'type' in params:
            sourceWorkspace["Provider"] = eKConverter.convertExtensionToName(params["type"])
        else:
            sourceWorkspace["Provider"] = 'WMS'
        return sourceWorkspace

    # For case Raster (GeoTiff)
    def __parseGdal(self, sourceString):
        sourceWorkspace = {}
        filename, fileExt = os.path.splitext(sourceString)
        fileExt = fileExt.strip('.')
        provider = eKConverter.convertExtensionToName(fileExt)
        if provider is not None:
            # Hash the source path to make a key
            keySource = hashlib.md5(sourceString.encode()).hexdigest()
            dstFolder = TEMP_LOCATION + '/source'
            # Check key to make sure that not upload the same source
            if keySource not in self.sourcePaths:
                sourceHelper = FileSourceHelper(fileExt, keySource)
                dstPath = sourceHelper.get(dstFolder, sourceString)
                self.sourcePaths[keySource] = dstPath
                sourceWorkspace["ConnectString"] = 'source\\' + keySource + '.' + fileExt
                sourceWorkspace["Provider"] = provider
        return sourceWorkspace

    def __parseMssql(self, sourceString):
        sourceWorkspace = {}
        dbname = eKMapCommonHelper.getByRegex(sourceString,r'dbname=\'(.*?)\'')
        host = eKMapCommonHelper.getByRegex(sourceString, r'host=(.*?)\s')
        user = eKMapCommonHelper.getByRegex(sourceString,r'user=\'(.*?)\'')
        password = eKMapCommonHelper.getByRegex(sourceString, r'password=\'(.*?)\'')
        connectString = r'Server={};Database={};UID={};PWD={}'
        connectString = connectString.format(host,dbname,user,password)
        sourceWorkspace["ConnectString"] = connectString

        tableName = eKMapCommonHelper.getByRegex(sourceString, r'table="(.*)"\."(.*?)"', 2)
        sourceWorkspace["TableName"] = tableName
        sourceWorkspace["Provider"] = "SQLServer"

        filter = eKMapCommonHelper.getByRegex(sourceString, r'sql=(.*?)$', 1)
        if filter is not None:
            self.currentSourceFilter = filter
        return sourceWorkspace

    # For Shapefile, SQLite, GeoJSON, GDB
    def __parseOgr(self, sourceString):
        sourceWorkspace = {}

        # The FORMAT of public source : (source path) | (layername) | (subset)
        # The source path has format: (path).(ext) 
        # the (ext) => Type of datasource
        publicSourceSplit = sourceString.split('|')
        sourcePath = publicSourceSplit[0]
        sourceBasename = os.path.basename(sourcePath).split('.')
        tableName = sourceBasename[0]
        provider = sourceBasename[-1]

        # Hash the source path to make a key
        keySource = hashlib.md5(sourcePath.encode()).hexdigest()
        dstFolder = TEMP_LOCATION + '/source'
        # Check key to make sure that not upload the same source
        if keySource not in self.sourcePaths:
            sourceHelper = FileSourceHelper(provider, tableName)
            dstPath = sourceHelper.get(dstFolder, sourcePath)
            self.sourcePaths[keySource] = dstPath

        ext = eKConverter.getExtension(provider)
        if provider is None:
            ext = 'shp'
            provider = 'Shapefile'
        basename = tableName + '.' + ext

        if provider == 'shp':
            path = 'source' + '\\' + tableName + '\\' + basename
        else:
            path = 'source' + '\\' + basename
        sourceWorkspace['ConnectString'] = path

        for sourceSplit in publicSourceSplit:
            if 'layername=' in sourceSplit:
                tableName = sourceSplit.split('layername=')[1]
            elif 'subset=' in sourceSplit:
                self.currentSourceFilter = sourceSplit.split('subset=')[1]

        sourceWorkspace['Provider'] = provider
        sourceWorkspace['TableName'] = tableName

        return sourceWorkspace