# -*- coding: utf-8 -*-

import datetime
import logging
import json

import tornado.web

from hmonitor.autofix import get_autofix_scripts
from hmonitor.common.constants import (UNBIND_AUTOFIX_SCRIPT_ACTION,
                                       AUTOFIX_STATUS)
from hmonitor.handlers import BaseHandler
from hmonitor.utils import convert_str_to_datetime

class ShowScriptsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        scripts = get_autofix_scripts()
        self.render("autofixscriptslist.html", scripts=scripts)


class BindScriptHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        def convert_list_to_dict(ls):
            d = dict()
            for l in ls:
                name = l["trigger_name"]
                d[name] = l
            return d

        scripts = get_autofix_scripts().keys()
        triggers = self.zabbix.get_triggers_info().keys()
        bindings = convert_list_to_dict(
            self.db.get_autofix_bindings()
        )
        self.render("autofixbinding.html", scripts=scripts,
                    triggers=triggers, bindings=bindings)

    @tornado.web.authenticated
    def post(self):
        new_script = self.request.arguments.get("v")[0]
        trigger_name = self.request.arguments.get("t")[0]
        username = self.get_user().get("name")
        try:
            if new_script == UNBIND_AUTOFIX_SCRIPT_ACTION:
                self.db.unbind_autofix(trigger_name)
            else:
                self.db.bind_autofix(trigger_name, username, new_script)
        except Exception as e:
            logging.exception(e)
            # TODO(tianhuan) Use another code here?
            raise tornado.httpclient.HTTPError(400)


class AutoFixHandler(BaseHandler):

    def post(self):
        event = json.loads(self.request.body)
        am = self.application.autofix_manager
        event["first_occur_time"] = convert_str_to_datetime(
            event["first_occur_time"]
        )
        event["last_occur_time"] = convert_str_to_datetime(
            event["last_occur_time"]
        )
        am.add_task(event)


class AutoFixStatHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        last_24_hours_logs = self.db.get_all_autofix_logs(last_day=1)
        last_7_days_logs = self.db.get_all_autofix_logs(last_day=7)

        last_7_day_success_logs = 0.0
        last_7_day_fixing_logs = 0.0
        last_7_day_failed_logs = 0.0
        for l in last_7_days_logs:
            if l["status"] == AUTOFIX_STATUS["success"]:
                last_7_day_success_logs += 1.0
            elif l["status"] == AUTOFIX_STATUS["fixing"]:
                last_7_day_fixing_logs += 1.0
            else:
                last_7_day_failed_logs += 1.0

        last_7_day_trend, keys = self._get_cataloged_logs(last_7_days_logs)

        self.render("autofixstat.html",
                    last_24_hours_logs=last_24_hours_logs,
                    last_7_days_logs=last_7_days_logs,
                    last_7_day_success_logs=last_7_day_success_logs,
                    last_7_day_fixing_logs=last_7_day_fixing_logs,
                    last_7_day_failed_logs=last_7_day_failed_logs,
                    last_7_day_trend=last_7_day_trend, keys=keys)

    def _get_cataloged_logs(self, logs):
        result = dict()
        keys = []
        now = datetime.datetime.now()
        today = datetime.datetime.strptime(now.strftime("%Y-%m-%d 23:59:59"),
                                           "%Y-%m-%d 23:59:59")
        for d in range(0, 7):
            day = today - datetime.timedelta(hours=24*d)
            day_add_1_day = day + datetime.timedelta(hours=24)
            k = day.strftime("%Y-%m-%d")
            keys.append(k.strip())
            result[k] = dict(
                success=0,
                failed=0,
                fixing=0
            )
            for l in logs:
                if (l["begin_time"] < day_add_1_day and
                        l["begin_time"] >= day):
                    if l["status"] == AUTOFIX_STATUS["success"]:
                        result[k]["success"] += 1
                    elif l["status"] == AUTOFIX_STATUS["failed"]:
                        result[k]["failed"] += 1
                    elif l["status"] == AUTOFIX_STATUS["fixing"]:
                        result[k]["fixing"] += 1
        return result, keys

