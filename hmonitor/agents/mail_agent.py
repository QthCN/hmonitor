import logging

from hmonitor.agents import BaseAgent
from hmonitor.utils import is_in_working_time_now
from hmonitor.utils.executor import get_executor
from hmonitor.utils.mail_lib import MailProxy

class MailAgent(BaseAgent):

    def __init__(self, db, executor, api_user, api_key, sender, endpoint):
        super(MailAgent, self).__init__(db)
        self.mail_proxy = MailProxy(api_user=api_user,
                                    api_key=api_key,
                                    sender=sender,
                                    endpoint=endpoint)
        self.executor_driver_name = executor
        self.executor = get_executor(executor)

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
        logging.debug("SEND MSG {m} TO {ma}".format(m=msg, ma=mail))
        result = self.mail_proxy.send(
            subject="[ALERT] {0}".format(event["trigger_name"]),
            msg=msg,
            to=mail
        )
        if result is False:
            logging.error("SEND MAIL FAILED, MSG: {m}".format(m=msg))
            return False
        self.db.record_alert_msg(event["trigger_name"], event["hostname"],
                                 mail=mail)
        return True

    def _handle_event(self, event):
        msg = self.get_alert_msg(event)
        users_id = self.db.get_users_id_by_trigger_name(event["trigger_name"])
        for user_id in users_id:
            user = self.db.get_user_by_id(user_id)
            #self._do_send_sms(user.get("mail", ""), msg, event)
