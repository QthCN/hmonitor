import logging

from hmonitor.agents import BaseAgent

class MailAgent(BaseAgent):

    def __init__(self):
        super(MailAgent, self).__init__()

    def do_task(self):
        while True:
            event = self.queue.get()
            logging.debug("MAIL AGENT GET EVENT: {0}".format(event))
            self.handle_event(event)

    def handle_event(self, event):
        # TODO(tianhuan)
        pass
