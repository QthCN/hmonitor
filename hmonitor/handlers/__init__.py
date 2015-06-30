# -*- coding: utf-8 -*-
import logging

from tornado.options import options
import tornado.web

from hmonitor.models.db import HMonitorDB
from hmonitor.utils.zabbix_lib import ZabbixProxy


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.db = HMonitorDB(mysql_user=options.mysql_user,
                             mysql_passwd=options.mysql_password,
                             mysql_host=options.mysql_host,
                             mysql_database=options.mysql_database)
        self.zabbix = ZabbixProxy(username=options.zabbix_user,
                                  password=options.zabbix_password,
                                  url=options.zabbix_url)

    def get_current_user(self):
        return self.get_secure_cookie("mail")

    def get_user(self):
        mail = self.get_secure_cookie("mail")
        user = self.db.get_user_by_mail(mail)
        return user
