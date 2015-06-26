import logging

from hmonitor.agents import BaseAgent
import hmonitor.common.constants as constants

class SmsAgent(BaseAgent):

    def __init__(self, db):
        super(SmsAgent, self).__init__(db)

    def do_task(self):
        while True:
            event = self.queue.get()
            logging.debug("SMS AGENT GET EVENT: {0}".format(event))
            try:
                self.handle_event(event)
            except Exception as e:
                logging.exception(e)

    def handle_event(self, event):
        if event["severity"] not in (constants.ZBX_SEVERITY_MAP["Disaster"],
                                     constants.ZBX_SEVERITY_MAP["High"]):
            logging.debug("IT IS NOT A DISASTER OR HIGH SEVERITY EVENT, "
                          "IGNORE IT.")
        else:
            self._handle_event(event)

    def _do_send_sms(self, phone, msg, event):
        # TODO(tianhuan) send msg here
        logging.debug("SEND MSG {m} TO {p}".format(m=msg, p=phone))
        self.db.record_alert_msg(event["trigger_name"], event["hostname"],
                                 phone=phone)

    def _handle_event(self, event):
        msg = self.get_alert_msg(event)
        users_id = self.db.get_users_id_by_trigger_name(event["trigger_name"])
        for user_id in users_id:
            user = self.db.get_user_by_id(user_id)
            self._do_send_sms(user.get("phone", ""), msg, event)
