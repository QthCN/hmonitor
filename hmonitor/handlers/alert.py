import json
import logging

from tornado.options import options

import hmonitor.common.constants as constants
from hmonitor.handlers import BaseHandler
from hmonitor.models.db import HMonitorDB


class AlertHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        super(AlertHandler, self).__init__(*args, **kwargs)
        self.db = HMonitorDB(mysql_user=options.mysql_user,
                             mysql_passwd=options.mysql_password,
                             mysql_host=options.mysql_host,
                             mysql_database=options.mysql_database)

    def post(self):
        request_body = json.loads(self.request.body)
        logging.debug("GET ZABBIX MSG: {0}".format(request_body))

        trigger_name = request_body.get("text", "").strip()
        hostname = request_body.get("resource", "").strip()
        event = request_body.get("event", "").strip()
        value = request_body.get("value", "").strip()

        if not trigger_name.startswith(constants.TRIGGER_PREFIX):
            pass
        else:
            self.db.record_trigger_event(trigger_name=trigger_name,
                                         hostname=hostname,
                                         event=event,
                                         value=value)
