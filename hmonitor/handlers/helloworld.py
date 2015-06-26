from hmonitor.handlers import BaseHandler
from hmonitor.utils.zabbix_lib import ZabbixProxy
from hmonitor.models.db import HMonitorDB

class HelloWorldHandler(BaseHandler):

    def get(self):
        zp = ZabbixProxy(username="Admin",
                         password="zabbix",
                         url="http://127.0.0.1/zabbix")
        print zp.get_triggers()

        db = HMonitorDB(mysql_user="root",
                       mysql_passwd="rootroot",
                       mysql_host="127.0.0.1",
                       mysql_database="hmonitor")
        print db.get_triggers_id_by_user_id(1)
        print db.check_password_by_mail("thuanqin@163.com", "helloworld")
        db.unbind_triggers_with_user_id(1, 23)

        self.render("helloworld.html")
