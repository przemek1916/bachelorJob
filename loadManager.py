__author__ = 'przemek'
import multiprocessing
import subprocess
import re
import logging
from threading import Thread
from threading import Event
from threading import RLock
from time import sleep
from Queue import Empty
from loadManagerExceptions import NoMoreJobException

logging.basicConfig(filename='/n/home/pteodorski/loadManager/loadManager.log', level=logging.DEBUG, format='%(levelname)s %(asctime)s:%(message)s')

event = None
load_reg_expr = 'load\saverage:(\s[0-9]\.[0-9]{2},?){3}'
numberExpr = '[0-9]\.[0-9]{2}'
freeNodesCommand = 'pbsnodes -l free | cut -f 1 -d " "'
loadManager = None
loadTimeout = 60
loadaveCoefficient = 1


def getLoadManager():
    global loadManager
    if loadManager is None:
        loadManager = LoadManager()
        return loadManager
    else:
        return loadManager


#resultInfo is the name of the file and nodename on which work was done and
def _callback(resultInfo):
    t = Thread(target=_updateAfterFinishJob, (resultInfo,))
    t.start()


def _parseInfo(info):
    tab = re.split('#', info)
    return tab[0], tab[1]


def _updateAfterFinishJob(resultInfo):
    global loadManager
    nodeName, jobName = _parseInfo(resultInfo)
    loadManager.releaseProcessNode(nodeName, jobName)


def initJob(self, args):
    command = 'dsh -m '+args[0]+' "/n/home/pteodorski/siec3/Network 1>/dev/null"'
    logging.info('submit job with file %s on node %s', args[1], args[0])
    subprocess.check_call([command], shell=True)
    return args[0]


def _startEvent():
    global event
    event = Event()


def _finishEvent():
    global event
    event.set()


class LoadManager:

    getItemTimeout = 30
    clusterNodes = {}

    def __init__(self):
        self.regEx = re.compile(load_reg_expr)
        self.numberRegEx = re.compile(numberExpr)
        self.getFreeNodes()
        self.isEmptyQueue = False
        #self.submitJobLock = RLock()
        #self.counterProcessLock = RLock()
        self.reentrantLock = RLock()

    def getFreeNodes(self):
        process = subprocess.Popen([freeNodesCommand], shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        nodes = re.split('\n', out)
        if nodes[len(nodes) - 1] == '':
            nodes = nodes[:-1]
        #nodes is a list of free nodes
        for n in nodes:
            loadave = self.checkNodeLoad(n)
            d = {}
            d['loadave'] = loadave
            d['processes'] = 0
            #d['lock'] = RLock()
            self.clusterNodes[n] = d

    def __call__(self, *args, **kwargs):
        self.queue = args[0]
        self.initialQueueSize = args[1]
        self.processesPerNode = args[2]
        self.numberOfFreeNodes = args[3]
        numberOfProcessesWorker = self.processesPerNode * self.numberOfFreeNodes
        if numberOfProcessesWorker > self.initialQueueSize:
            numberOfProcessesWorker = self.initialQueueSize
        self.processesPool = multiprocessing.Pool(self.initialQueueSize)
        """
        place to start begining tasks on nodes
        """
        self.startTasks()
        #event is finished when exception is thrown and then invoke set() method
        _startEvent()

    def releaseProcessNode(self, nodeName, finishedJobName):
        with self.reentrantLock: #self.currentProcessLock
            logging.info('release node %s', nodeName)
            self.clusterNodes[nodeName]['processes'] -= 1
            if not self.isThereAnyRunningProcess() and self.queue.empty():
                logging.info('queue is empty and all tasks were done, about to finish loadManager process')
                #TODO
                #set _startEvents.set to finish process
                pass
            else:
                if self.clusterNodes[nodeName]['processes'] == (self.processesPerNode - 1):
                    #self.manageNode(nodeName)
                    manageNodeThread = Thread(target=self.manageNode, kwargs={'nodeName': nodeName})
                    manageNodeThread.start()
                #else:
                    #pass
                    #another thread has been working on that

    def isThereAnyRunningProcess(self):
        for node in self.clusterNodes.keys():
            if self.clusterNodes[node]['processes'] != 0:
                return True
        return False

    def manageNode(self, nodeName, *args, **kwargs):
        #1 process = 1 unit of loadAve
        nodeName = nodeName
        currentLoadAve = self.checkNodeLoad(nodeName) # tuple
        global loadaveCoefficient
        loadave = loadaveCoefficient * currentLoadAve[0] #optionally use round()
        while loadave > self.processesPerNode:
            global loadTimeout
            sleep(loadTimeout)
            """
            self.manageNode(nodeName) recursive, but that was replaced with evaluating loadave once again
            and if statement was replaced with wihle loop
            """
            currentLoadAve = self.checkNodeLoad(nodeName)
            loadave = loadaveCoefficient * currentLoadAve[0]
        else:
            with self.reentrantLock: #self.currentProcessLock
                difference = 0
                if loadave < self.clusterNodes[nodeName]['processes']:
                    difference = self.processesPerNode - self.clusterNodes[nodeName]['processes']
                else:
                    difference = self.processesPerNode - int(loadave)
                for i in range(difference):
                    try:
                        self.submitJob(node=nodeName)
                    except NoMoreJobException:
                        return
            return

    def startTasks(self):
        """
        for now we assume that value '1' of load average means one process is running, '2' means two processes are running ...

        for n in self.clusterNodes:
            if round(self.clusterNodes[n]['loadave'][0]) < 0:
                for i in range(self.processesPerNode):
                    self.submitJob()
        """
        #sort nodes by loadave
        nodes = self.clusterNodes.keys()
        nodesNeedToManage = []
        for i in range(self.processesPerNode):
            global loadaveCoefficient
            if self.clusterNodes[nodes[i]]['loadave'][0] * loadaveCoefficient > (i + 1):
                if i == 0:
                    nodesNeedToManage.append(nodes[i])
            else:
                try:
                    self.submitJob(node=nodes[i])
                except NoMoreJobException:
                    return
        if not self.queue.empty():
            for n in nodesNeedToManage:
                self.manageNode(kwargs={'nodeName': n})

    def submitJob(self, node, jobArgs):
        try:
            self.reentrantLock.acquire()  #self.currentProcessLock
            task = self.queue.get(True, self.getItemTimeout)
            self.processesPool.apply_async(initJob, (node,), callback=_callback)
            self.clusterNodes[node]['processes'] += 1
        except Empty:
            self.isEmptyQueue = True
            raise NoMoreJobException('Queue is empty')
        finally:
            self.reentrantLock.release()

    def checkNodeLoad(self, nodeName):
        command = 'dsh -m ' + nodeName + ' uptime'
        process = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        result = re.search(load_reg_expr, out)
        loadave = result.group()
        return self.getLoadAve(loadave)

    def getLoadAve(self, loadaveText):
        numbers = re.findall(numberExpr, loadaveText)
        return tuple(numbers)


def Timer(*args, **kwargs):
    """Factory function to create a Timer object.

Timers call a function after a specified number of seconds:

t = Timer(30.0, f, args=[], kwargs={})
t.start()
t.cancel() # stop the timer's action if it's still waiting

 """
    return _Timer(*args, **kwargs)


class _Timer(Thread):
    """Call a function after a specified number of seconds:

        t = Timer(30.0, f, args=[], kwargs={})
        t.start()
        t.cancel() # stop the timer's action if it's still waiting

    """
    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()

 # Special thread class to represent the main thread
 # This is garbage collected through an exit handler