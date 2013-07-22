import asyncore
import socket
import asynchat
import protocol
import re

class asynchat_client_handler(asynchat.async_chat):

    def parseFileTree(self):
        message = self.ibuffer
        r = re.search(self.dirsExpr, message)
        if r is None:
            pass
            #raise some exception
        dirInfo = r.group()
        message = message[:-len(dirInfo)]
        dirsCount = int(dirInfo[protocol.DIRS_COUNT_REGEX_LEN:])
        if dirsCount>0:
            l = re.split(protocol.DIRECTORY_SEPARATOR, message)
            fList = None
            if len(l[dirsCount+1])>0:
                #files exist
                fList = re.split(protocol.FILE_SEPARATOR, l[dirsCount+1])[1:]
            self.gui.addTreePaths(l[0], l[1:dirsCount+1], fList)
        else :
            l = re.split(protocol.FILE_SEPARATOR, message)
            if len(l)>1:
                self.gui.addTreePaths(l[0], None, l[1:])
            #else rootPath has no content

    def setGuiActions(self):
        self.gui.setGuiActions(onExpand=self.getTreePath, closeConnection=self.closeConnection)

    def closeConnection(self):
        self.close()

    def getTreePath(self, parentPath):
        message = protocol.GET_SCORPION_PATHS+protocol.MESSAGE_TYPE_TERMINATOR
        message += parentPath+protocol.MESSAGE_END_TERMINATOR
        self.push(message)
        #self.push('GET_SCORPION_PATHS\r\n/home\r\n\r\n')

    #def handle_connect(self):
        #self.gui.testAddFiles('test_File')

    actions = { protocol.SEND_SCORPION_PATHS: parseFileTree}
    dirsExpr = re.compile(protocol.DIRS_COUNT_REGEX+'[0-9]*$')

    def __init__(self, host, gui):
        asynchat.async_chat.__init__(self)
        self.gui = gui
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect((host, 50007))
        self.ibuffer = ''
        self.obuffer = ''
        self.set_terminator(protocol.MESSAGE_END_TERMINATOR)
        self.setGuiActions()
        self.requestPattern = re.compile(protocol.REQUEST_PATTERN)

    #def getStartRootTree(self):
    #    self.push(protocol.GET_SCORPION_PATHS+protocol.MESSAGE_TYPE_TERMINATOR)

    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer += data

    def found_terminator(self):
        print('found terminator')
        request = re.search('^\w*\r\n', self.ibuffer)
        action = request.group()[:-protocol.MESSAGE_TYPE_TERMINATOR_LENGTH]
        self.ibuffer = self.ibuffer[len(action)+protocol.MESSAGE_TYPE_TERMINATOR_LENGTH:]
        self.handle_request(action)
        self.ibuffer=''

    def handle_request(self, action):
        self.actions[action](self)
