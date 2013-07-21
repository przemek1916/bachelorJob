__author__ = 'przemek'
from os import walk
import re

GET_SCORPION_PATHS = "GET_SCORPION_PATHS"
SEND_SCORPION_PATHS = "RECEIVE_SCORPION_PATHS"
DATA_TO_PROCESS = "DATA_TO_PROCESS"
FILE_SEPARATOR = "//"
DIRECTORY_SEPARATOR = "///"
MESSAGE_TYPE_TERMINATOR = "\r\n"
MESSAGE_TYPE_TERMINATOR_LENGTH = len(MESSAGE_TYPE_TERMINATOR)
MESSAGE_END_TERMINATOR = "\r\n\r\n"
MESSAGE_END_TERMINATOR_LENGTH=len(MESSAGE_END_TERMINATOR)
DIRS_COUNT_REGEX = 'dirs'
DIRS_COUNT_REGEX_LEN=len(DIRS_COUNT_REGEX)
REQUEST_PATTERN = '^\w*'+MESSAGE_TYPE_TERMINATOR
PORT=50007

REQUEST_WITHOUT_DATA = []

class simple_producer:
    def __init__ (self, data):
        self.data = data

    def more (self):
        if len (self.data) > 512:
            result = self.data[:512]
            self.data = self.data[512:]
            return result
        else:
            result = self.data
            self.data = ''
            return result

def getFileRootTree(rootPath):
    print('root path is: '+rootPath)
    tree = rootPath
    length = len(rootPath)+1
    dirsCounter = 0
    for root, dirs, files in walk(rootPath):
        for d in dirs:
            tree += DIRECTORY_SEPARATOR+d
            dirsCounter +=1
        if dirsCounter >0:
            tree += DIRECTORY_SEPARATOR
        for f in files:
            tree += FILE_SEPARATOR+f
        break
    tree +=DIRS_COUNT_REGEX+str(dirsCounter)
    """
        tree += root[length:]
        for i in files:
            tree += FILE_SEPARATOR+i
        tree += DIRECTORY_SEPARATOR
    """
    return tree
