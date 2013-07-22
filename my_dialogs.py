__author__ = 'przemek'
from PyQt4 import QtGui
from PyQt4 import QtCore
import re


class LogDialog(QtGui.QDialog):

    def __init__(self, parent=None, username=None):
        super(LogDialog, self).__init__(parent)
        #self.browser = QtGui.QTextBrowser()
        self.usernameInput = QtGui.QLineEdit(
            username)
        self.usernameInput.selectAll()
        self.password = QtGui.QLineEdit()
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        labelLayout = QtGui.QVBoxLayout()
        self.userNameLabel = QtGui.QLabel('Uzytkownik', self)
        self.passwordLabel = QtGui.QLabel('Haslo', self)

        """
        gridLayout
        """
        grid = QtGui.QGridLayout()
        grid.addWidget(self.userNameLabel, 0, 0)
        grid.addWidget(self.passwordLabel, 1, 0)
        grid.addWidget(self.password, 1, 1)
        grid.addWidget(self.usernameInput, 0, 1)

        self.okButton = QtGui.QPushButton('Zaloguj')
        self.cancelButton = QtGui.QPushButton('Anuluj')

        grid.addWidget(self.okButton, 2, 0)
        grid.addWidget(self.cancelButton, 2, 1)

        self.setLayout(grid)
        #self.lineedit.setFocus()
        #self.connect(self.lineedit,SIGNAL("returnPressed()"),self.updateUi)
        self.setWindowTitle("Logowanie do jw")


class LocalTreeFilesView(QtGui.QTreeView):

    def __init__(self, parent=None, filesList=None):
        super(LocalTreeFilesView, self).__init__()
        self.itemModel = QtGui.QStandardItemModel()
        directoryPixmap = QtGui.QPixmap()
        isLoaded = directoryPixmap.load("/home/przemek/Pulpit/folder_icon.jpg")
        #self.directoryIcon = QtGui.QIcon(directoryPixmap)
        self.directoryIcon = QtGui.QIcon.fromTheme('folder')
        self.fileIcon = QtGui.QIcon.fromTheme('text-x-generic')
        self.setModel(self.itemModel)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        if filesList is not None:
            self.addFilesRecursively(filesList, self.itemModel)
        self.itemModel.setHorizontalHeaderLabels(['Pliki'])
        self.selModel = self.selectionModel()
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.PATHS = []

    def ifPathIsAlreadyIncluded(self, path):
        if path in self.PATHS:
            return True
        chunks = re.split('/', path)
        while len(chunks)>2:
            cutLen = len(chunks.pop())+1 #+1 because of '/'
            path = path[:-cutLen]
            if path in self.PATHS:
                return True
        return False

    def addTreePaths(self, dirs, files, item):
        if item.hasChildren():
            self.itemModel.removeRow(0, item.index())
        if dirs is not None:
            for d in dirs:
                directory = QtGui.QStandardItem(self.directoryIcon, d)
                item.appendRow(directory)
                empty = QtGui.QStandardItem('')
                directory.appendRow(empty)
        if files is not None:
            for f in files:
                file = QtGui.QStandardItem(self.fileIcon, f)
                item.appendRow(file)

    def addPath(self, path, mode):
        if self.ifPathIsAlreadyIncluded(path) is False:
            self.PATHS.append(path)
            if mode=='directory':
                directory = QtGui.QStandardItem(self.directoryIcon, path)
                self.itemModel.appendRow(directory)
                empty = QtGui.QStandardItem('')
                directory.appendRow(empty)
            else:
                file = QtGui.QStandardItem(self.fileIcon, path)
                self.itemModel.appendRow(file)

    def addSelectedPaths(self, dictionary):
        for k in dictionary.keys():
            self.addPath(k, dictionary[k])

    def addFilesRecursively(self, filesList, parentItem=None):
        if type(filesList) is list:
            for i in filesList:
                if type(i) is list:
                    directory = QtGui.QStandardItem(self.directoryIcon, i[0])
                    if parentItem is None:
                        self.itemModel.appendRow(directory)
                    else:
                        parentItem.appendRow(directory)
                    if len(i)>1:
                        self.addFilesRecursively(i[1:], directory)
                else :
                    file = QtGui.QStandardItem(self.fileIcon, i)
                    if parentItem is None:
                        self.itemModel.appendRow(file)
                    else:
                        parentItem.appendRow(file)
        else :
            file = QtGui.QStandardItem(self.fileIcon, filesList)
            if parentItem is None:
                self.itemModel.appendRow(file)
            else:
                parentItem.appendRow(file)

    def filterIndexesToRemove(self, indexes):
        temp = {}
        for index in indexes:
            dItem = self.itemModel.itemFromIndex(index)
            path = ''
            while dItem is not None:
                path = '/'+str(dItem.text())+path
                dItem = dItem.parent()
            for k in temp.keys():
                if len(k)>len(path):
                    if k[:len(path)]==path:
                        del temp[k]
                else:
                    if path[:len(k)]==k:
                        break
            else:
                temp[path]=index #or dItem?
        indexList = temp.values()
        indexList.sort(key=lambda x: x.row(), reverse=True)
        return indexList

    def removeSelectedFiles(self):
        indexes = self.selModel.selectedIndexes()
        filteredIndexes = self.filterIndexesToRemove(indexes)
        print(filteredIndexes)
        for index in filteredIndexes:
            #print(str(index.row())+" that was row, and the column is: "+str(index.column()))
            #print(str(index.parent().text()))
            #print(parentIndex.isValid())
            print('item row: '+str(index.row()))
            isDeleted = self.itemModel.removeRow(index.row(), index.parent())


class RemoteTreeFilesView(QtGui.QTreeView):

    def __init__(self, parent=None, filesList=None):
        super(RemoteTreeFilesView, self).__init__()
        self.itemModel = QtGui.QStandardItemModel()
        #self.expanded.connect(self.getContentsOnExpand)
        directoryPixmap = QtGui.QPixmap()
        isLoaded = directoryPixmap.load("/home/przemek/Pulpit/folder_icon.jpg")
        #self.directoryIcon = QtGui.QIcon(directoryPixmap)
        self.directoryIcon = QtGui.QIcon.fromTheme('folder')
        self.fileIcon = QtGui.QIcon.fromTheme('text-x-generic')
        self.setModel(self.itemModel)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        if filesList is not None:
            self.addFilesRecursively(filesList, self.itemModel)
        self.itemModel.setHorizontalHeaderLabels(['Skorpion'])
        self.selModel = self.selectionModel()
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    def getSelectedFilesPath(self):
        d = {}
        indexes = self.selModel.selectedIndexes()
        for index in indexes:
            selectedFile = self.itemModel.itemFromIndex(index)
            #check if it is file or directory
            icon = selectedFile.icon()
            iconName = str(icon.name())
            path=''
            while selectedFile is not None:
                path = '/'+str(selectedFile.text())+path
                selectedFile = selectedFile.parent()
            path = path[1:]
            if iconName=='folder':
                d[path]='directory'
            elif iconName=='text-x-generic':
                d[path]='file'
        return d

    def addTreePaths(self, dirs, files, item):
        if item.hasChildren():
            self.itemModel.removeRow(0, item.index())
        if dirs is not None:
            for d in dirs:
                directory = QtGui.QStandardItem(self.directoryIcon, d)
                item.appendRow(directory)
                empty = QtGui.QStandardItem('')
                directory.appendRow(empty)
        if files is not None:
            for f in files:
                file = QtGui.QStandardItem(self.fileIcon, f)
                item.appendRow(file)

    def addFilesRecursively(self, filesList, parentItem=None):
        if type(filesList) is list:
            for i in filesList:
                if type(i) is list:
                    directory = QtGui.QStandardItem(self.directoryIcon, i[0])
                    if parentItem is None:
                        self.itemModel.appendRow(directory)
                    else:
                        parentItem.appendRow(directory)
                    if len(i)>1:
                        self.addFilesRecursively(i[1:], directory)
                else :
                    file = QtGui.QStandardItem(self.fileIcon, i)
                    if parentItem is None:
                        self.itemModel.appendRow(file)
                    else:
                        parentItem.appendRow(file)
        else :
            file = QtGui.QStandardItem(self.fileIcon, filesList)
            if parentItem is None:
                self.itemModel.appendRow(file)
            else:
                parentItem.appendRow(file)