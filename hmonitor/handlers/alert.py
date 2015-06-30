# -*- coding: utf-8 -*-

import json
import logging

import hmonitor.common.constants as constants
from hmonitor.handlers import BaseHandler


class AlertHandler(BaseHandler):

    def post(self):
        request_body = json.loads(self.request.body)
        logging.debug("GET ZABBIX MSG: {0}".format(request_body))

        trigger_name = request_body.get("text", "").strip()
        hostname = request_body.get("resource", "").strip()
        event = request_body.get("event", "").strip()
        value = request_body.get("value", "").strip()
        severity = request_body.get("severity", "").strip()

        if not trigger_name.startswith(constants.TRIGGER_PREFIX):
            pass
        else:
            self.db.record_trigger_event(trigger_name=trigger_name,
                                         hostname=hostname,
                                         event=event,
                                         value=value,
                                         severity=severity)
