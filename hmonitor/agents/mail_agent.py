import logging

from hmonitor.agents import BaseAgent
from hmonitor.utils import is_in_working_time_now

class MailAgent(BaseAgent):

    def __init__(self, db):
        super(MailAgent, self).__init__(db)

    def do_task(self):
        while True:
            event = self.queue.get()
            logging.debug("MAIL AGENT GET EVENT: {0}".format(event))
            try:
                self.handle_event(event)
            except Exception as e:
                logging.exception(e)

    def handle_event(self, event):
        if is_in_working_time_now():
            self._handle_event(event)
        else:
            logging.debug("NOT IN WORKING TIME, IGNORE THIS EVENT.")

    def _do_send_sms(self, mail, msg, event):
        # TODO(tianhuan) send msg here
        logging.debug("SEND MSG {m} TO {ma}".format(m=msg, ma=mail))
        self.db.record_alert_msg(event["trigger_name"], event["hostname"],
                                 mail=mail)

    def _handle_event(self, event):
        msg = self.get_alert_msg(event)
        users_id = self.db.get_users_id_by_trigger_name(event["trigger_name"])
        for user_id in users_id:
            user = self.db.get_user_by_id(user_id)
            self._do_send_sms(user.get("mail", ""), msg, event)
