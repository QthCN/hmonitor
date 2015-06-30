# -*- coding: utf-8 -*-
import Queue
import threading

class BaseAgent(object):

    def __init__(self, db):
        self.queue = Queue.Queue()
        self.db = db

    def run(self):
        t = threading.Thread(target=self.do_task)
        t.daemon = True
        t.start()
        
    def do_task(self):
        pass

    def initialize(self):
        pass

    def notice(self, event):
        self.queue.put(event)

    def get_alert_msg(self, event):
        trigger_name = event["trigger_name"]
        hostname = event["hostname"]
        value = event["value"]
        msg = "[ALERT] {h} in {t}, value is {v}".format(h=hostname,
                                                        t=trigger_name,
                                                        v=value)
        return msg
