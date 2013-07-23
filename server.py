import asyncore
import socket
import asynchat
import protocol
import re
import logging
from multiprocessing import Process
from multiprocessing import Manager

manager = Manager()
queue = 
processName = 'loadManager'
managerProcess = None

class asynchat_handler(asynchat.async_chat):

	def submitTasks(self):
		logging.info('submitTasks')
		tasks = re.split(protocol.FILE_SEPARATOR, self.ibuffer)
		"""
		prepare jobs to submit

		check if process exist and is doing jobs = true #tip: use Process'es method is_alive()
			put tasks to queue
		      else
			start new process
		"""
		global managerProcess
		global queue
		if managerProcess.is_alive() is True:
			for t in tasks:
				queue.put(t)
		else:
			global porcessName
			#initialize queue
			for t in tasks:
				queue.put(t)
			loadManager = LoadManager()
			managerProcess = Process(target=loadManager, name=processName, args=(queue, len(tasks), processesPerNode))
			process.start()
	
	def sendFileTreePaths(self):
		logging.info('send message')
		rootPath = self.ibuffer
		message = protocol.SEND_SCORPION_PATHS+protocol.MESSAGE_TYPE_TERMINATOR
		message += protocol.getFileRootTree(rootPath)+protocol.MESSAGE_END_TERMINATOR
		producer = protocol.simple_producer(message)
		self.push_with_producer(producer)

	actions = {protocol.GET_SCORPION_PATHS: sendFileTreePaths, protocol.SUBMIT_TASKS: submitTasks}
	
	def __init__(self, sock, addr):
        	asynchat.async_chat.__init__(self, sock=sock)
        	self.addr = addr
        	self.ibuffer = ''
        	self.obuffer = ''
        	self.set_terminator(protocol.MESSAGE_END_TERMINATOR)
		self.requestPattern = re.compile(protocol.REQUEST_PATTERN)

	def collect_incoming_data(self, data):
        	"""Buffer the data"""
        	self.ibuffer += (data)

	def found_terminator(self):
		logging.info('found terminator')
		request = re.search(self.requestPattern, self.ibuffer)
		action = request.group()[:-protocol.MESSAGE_TYPE_TERMINATOR_LENGTH]
		self.ibuffer = self.ibuffer[len(action)+protocol.MESSAGE_TYPE_TERMINATOR_LENGTH:]
		self.handle_request(action)
            	self.ibuffer=''

	def handle_request(self, action):
		self.actions[action](self)

class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = asynchat_handler(sock, addr)

server = EchoServer('localhost', protocol.PORT)
asyncore.loop()
