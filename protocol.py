__author__ = 'przemek'
from os import walk
import re

GET_SCORPION_PATHS = "GET_SCORPION_PATHS"
SEND_SCORPION_PATHS = "RECEIVE_SCORPION_PATHS"
SUBMIT_TASKS = "SUBMIT_TASKS"
GET_WORK_STATE_INFO = "GET_WORK_STATE_INFO"
SEND_CURRENT_STATE_INFO = "SEND_CURRENT_STATE_INFO"
DATA_TO_PROCESS = "DATA_TO_PROCESS"
FILE_SEPARATOR = "//"
DIRECTORY_SEPARATOR = "///"
LIST_SEPARATOR = "////"
MESSAGE_TYPE_TERMINATOR = "\r\n"
MESSAGE_TYPE_TERMINATOR_LENGTH = len(MESSAGE_TYPE_TERMINATOR)
MESSAGE_END_TERMINATOR = "\r\n\r\n"
MESSAGE_END_TERMINATOR_LENGTH=len(MESSAGE_END_TERMINATOR)
DIRS_COUNT_REGEX = 'dirs'
DIRS_COUNT_REGEX_LEN=len(DIRS_COUNT_REGEX)
REQUEST_PATTERN = '^\w*'+MESSAGE_TYPE_TERMINATOR
PORT=50007

REQUEST_WITHOUT_DATA = []

def filterWorkStateInfo(done, running, enqueue):
	for e in enqueue:
		if running.__contains__(e):
			enqueue.remove(e)
	for r in running:
		if done.__contains(r):
			running.remove(r)

def wrapWorkStateInfo(done, running, enqueue):
	filterWorkStateInfo(done, running, enqueue)
	global FILE_SEPARATOR, DIRECTORY_SEPARATOR
	s = ''

	s1 = ''
	for d in done:
		s1 += d+FILE_SEPARATOR
	s1 = s1[:-len(FILE_SEPARATOR)]
	s += s1+LIST_SEPARATOR

	s2 = ''
	for r in running:
		s2 += r+FILE_SEPARATOR
	s2 = s2[:-len(FILE_SEPARATOR)]
	s += s2+LIST_SEPARATOR

	s3 = ''
	for e in enqueue:
		s3 += e+FILE_SEPARATOR
	s3 = s3[:-len(FILE_SEPARATOR)]
	s += s3
	return s

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
