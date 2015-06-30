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

