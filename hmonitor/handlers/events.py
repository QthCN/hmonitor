import logging

import tornado.web

from hmonitor.handlers import BaseHandler
from hmonitor.utils.zabbix_lib import ZabbixProxy

class MyEventsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("myevents.html")
