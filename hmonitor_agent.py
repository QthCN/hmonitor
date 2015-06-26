import datetime
import logging
import time

import tornado
from tornado.options import define, options

from hmonitor.agents.mail_agent import MailAgent
from hmonitor.agents.sms_agent import SmsAgent
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
        self.events_notification_history = dict()
        self.db = HMonitorDB(mysql_user=options.mysql_user,
                             mysql_passwd=options.mysql_password,
                             mysql_host=options.mysql_host,
                             mysql_database=options.mysql_database)

        self.notification_agents = [MailAgent(db=self.db),
                                    SmsAgent(db=self.db)]

    def initialize(self):
        for agent in self.notification_agents:
            agent.initialize()

    def _auto_fix(self, event):
        # TODO(tianhuan) add auto fix here
        logging.debug("BEGIN AUTO FIX ON EVENT: {0}".format(event))
        return False

    def _get_history_key(self, event):
        return "{t}_{h}".format(t=event["trigger_name"], h=event["hostname"])

    def _is_history_expired(self, notice_obj):
        now = datetime.datetime.now()
        return (now - notice_obj["last_send_time"]).seconds > 300

    def _do_actions(self, events):
        for event in events:
            if self._auto_fix(event):
                # TODO(tianhuan) send notification here?
                continue
            else:
                h_key = self._get_history_key(event)
                notice_obj = self.events_notification_history.get(h_key, None)
                if (notice_obj and
                        not self._is_history_expired(notice_obj)):
                    logging.debug("{e}'s history is not expired".format(
                        e=h_key
                    ))
                    continue
                else:
                    notice_obj = dict(last_send_time=datetime.datetime.now())
                    self.events_notification_history[h_key] = notice_obj

                    for agent in self.notification_agents:
                        agent.notice(event)

    def _run_notification_agents(self):
        for agent in self.notification_agents:
            agent.run()

    def run(self):
        self._run_notification_agents()
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
    agent.initialize()
    agent.run()


if __name__ == "__main__":
    main()
