import logging
import time

import tornado
from tornado.options import define, options

from hmonitor.models.db import HMonitorDB


define("mysql_host", default="127.0.0.1:3306", help="hmonitor database host")
define("mysql_database", default="hmonitor", help="hmonitor database name")
define("mysql_user", default="root", help="hmonitor database user")
define("mysql_password", default="rootroot", help="hmonitor database password")
define("zabbix_user", default="Admin", help="Zabbix user name")
define("zabbix_password", default="zabbix", help="Zabbix password")
define("zabbix_url", default="http://127.0.0.1/zabbix", help="Zabbix URL")


class Agent(object):

    def __init__(self, mysql_host, mysql_database, mysql_user, mysql_password,
                 zabbix_user, zabbix_password, zabbix_url):
        self.mysql_host = mysql_host
        self.mysql_database = mysql_database
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.zabbix_user = zabbix_user
        self.zabbix_password = zabbix_password
        self.zabbix_url = zabbix_url
        self.db = HMonitorDB(mysql_user=options.mysql_user,
                             mysql_passwd=options.mysql_password,
                             mysql_host=options.mysql_host,
                             mysql_database=options.mysql_database)

    def _do_actions(self, events):
        # TODO
        pass

    def run(self):
        while True:
            # Expire events
            self.db.expire_trigger_events()
            # Trigger actions
            events = self.db.get_trigger_events_in_problem()
            logging.debug("Events in problem:\n {0}".format(events))
            self._do_actions(events)
            time.sleep(30)


def main():
    tornado.options.parse_command_line()
    agent = Agent(mysql_host=options.mysql_host,
                  mysql_database=options.mysql_database,
                  mysql_user=options.mysql_user,
                  mysql_password=options.mysql_password,
                  zabbix_user=options.zabbix_user,
                  zabbix_password=options.zabbix_password,
                  zabbix_url=options.zabbix_url)
    agent.run()

if __name__ == "__main__":
    main()
