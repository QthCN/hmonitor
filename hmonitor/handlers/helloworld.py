from hmonitor.handlers import BaseHandler
from hmonitor.utils.zabbix_lib import ZabbixProxy

class HelloWorldHandler(BaseHandler):

    def get(self):
        zp = ZabbixProxy(username="Admin",
                         password="zabbix",
                         url="http://127.0.0.1/zabbix")
        print zp.get_triggers()
        self.render("helloworld.html")
