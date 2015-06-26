import logging

import tornado.web

from hmonitor.handlers import BaseHandler
from hmonitor.utils.zabbix_lib import ZabbixProxy
from hmonitor.models.db import HMonitorDB

class HelloWorldHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        zp = ZabbixProxy(username="Admin",
                         password="zabbix",
                         url="http://127.0.0.1/zabbix")
        print zp.get_triggers()

        self.render("base.html", page_name="message")
