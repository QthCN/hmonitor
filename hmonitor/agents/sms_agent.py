# -*- coding: utf-8 -*-
import logging

from hmonitor.agents import BaseAgent
from hmonitor.utils.executor import get_executor
from hmonitor.utils.sms_lib import SmsProxy
import hmonitor.common.constants as constants

class SmsAgent(BaseAgent):

    def __init__(self, db, executor, username, password,
                 epid, endpoint, charset="gb2312"):
        super(SmsAgent, self).__init__(db)
        self.sms_proxy = SmsProxy(username=username,
                                  password=password,
                                  epid=epid,
                                  endpoint=endpoint,
                                  charset=charset)
        self.executor_driver_name = executor
        self.executor = get_executor(executor)

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
        logging.debug("SEND MSG {m} TO {p}".format(m=msg, p=phone))
        result = self.sms_proxy.send(msg=msg, to=phone)
        if result is False:
            logging.error("SEND SMS FAILED, MSG: {m}".format(m=msg))
            return False
        self.db.record_alert_msg(event["trigger_name"], event["hostname"],
                                 phone=phone)
        return True

    def _handle_event(self, event):
        msg = self.get_alert_msg(event)
        users_id = self.db.get_users_id_by_trigger_name(event["trigger_name"])
        for user_id in users_id:
            user = self.db.get_user_by_id(user_id)
            #self._do_send_sms(user.get("phone", ""), msg, event)
