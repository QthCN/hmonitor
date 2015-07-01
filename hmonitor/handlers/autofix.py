# -*- coding: utf-8 -*-

import logging
import json

import tornado.web

from hmonitor.autofix import get_autofix_scripts
from hmonitor.common.constants import UNBIND_AUTOFIX_SCRIPT_ACTION
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
