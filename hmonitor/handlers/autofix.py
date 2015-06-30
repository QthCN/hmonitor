# -*- coding: utf-8 -*-

import logging

import tornado.web

from hmonitor.autofix import get_autofix_scripts
from hmonitor.handlers import BaseHandler

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
