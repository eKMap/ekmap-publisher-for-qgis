from qgis.core import QgsApplication
from ..ekmap_converter import eKConverter
from ..ekmap_logger import eKLogger
from ..ekmap_common import *

import subprocess

class FileSourceHelper():

    def __init__(self, extension, fileName):
        self.__provider = eKConverter.convertExtensionToName(extension)
        self.__fileName = fileName

    def get(self, destPath, sourcePath):
        self.__destPath = destPath
        self.__sourcePath = sourcePath

        os.makedirs(destPath, exist_ok=True)
        if self.__provider is None:
            methodName = '_getOther'
        else:
            methodName = '_get' + self.__provider
        method = getattr(self, methodName, lambda: None)
        return method()

    # Name of these following method must be the same
    # with the return value in convertExtensionToName of eKConverter
    def _getShapefile(self):
        # Path: (Folder)/(Basename).shp
        # Also get other file with same basename .cpg, .dbf, .prj, .sbn, ...
        folderPath = self.__destPath + '/' + self.__fileName
        os.makedirs(folderPath, exist_ok=True)
        sourceDir = os.path.dirname(self.__sourcePath)
        for filePath in self.__getFilesPathInDirWithSameName(sourceDir, self.__fileName):
            shutil.copy2(filePath, folderPath)
        return folderPath
    def _getGeoJSON(self):
        # Path: (Folder)/(Basename).json
        dstPath = self.__destPath + '/' + self.__fileName + '.json'
        shutil.copyfile(self.__sourcePath, dstPath)
        return dstPath
    def _getGDB(self):
        # Path: (Folder)/(Basename).gdb
        # (Basename).gdb is folder
        # Need copy all
        folderPath = self.__destPath + '/' + self.__fileName + '.gdb'
        os.makedirs(folderPath, exist_ok=True)
        for root, directories, files in os.walk(self.__sourcePath):
            for filename in files:
                filePath = os.path.join(root, filename)
                shutil.copy2(filePath, folderPath)
        return folderPath
    def _getSQLite(self):
        # Path: (Folder)/(Basename).sqlite
        dstPath = self.__destPath + '/' + self.__fileName + '.sqlite'
        shutil.copyfile(self.__sourcePath, dstPath)
        return dstPath
    def _getGeoTiff(self):
        # Path: (Folder)/(Basename).tif
        dstPath = self.__destPath + '/' + self.__fileName + '.tif'
        shutil.copyfile(self.__sourcePath, dstPath)
        return dstPath
    def _getOther(self):
        eKLogger.log("Other")
        folderPath = self.__destPath + '/' + self.__fileName
        eKLogger.log("Folder path")
        ogr2ogr = QgsApplication.prefixPath().rstrip('apps/qgis') + '/bin/ogr2ogr.exe'
        command = [ogr2ogr, '-f', 'ESRI Shapefile', folderPath, self.__sourcePath]
        eKLogger.log(command)
        subprocess.call(command, shell=True)
        return folderPath

    # Lấy tất cả các file trong thư mục có cùng tên
    def __getFilesPathInDirWithSameName(self, directory, name):
        filePaths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                if filename.split(".")[0] == name:
                    filePath = os.path.join(root, filename)
                    filePaths.append(filePath)
        return filePaths