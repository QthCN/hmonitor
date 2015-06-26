import Queue
import threading

class BaseAgent(object):

    def __init__(self, *args, **kwargs):
        self.queue = Queue.Queue()

    def run(self):
        threading.Thread(target=self.do_task).start()
        
    def do_task(self):
        pass

    def initialize(self):
        pass

    def notice(self, event):
        self.queue.put(event)
