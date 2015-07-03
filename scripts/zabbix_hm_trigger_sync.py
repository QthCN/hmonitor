# -*- coding: utf-8 -*-

import logging

import tornado
from tornado.options import define, options

from hmonitor.models.db import HMonitorDB
from hmonitor.utils.zabbix_lib import ZabbixProxy


#MySQL
define("mysql_host", default="127.0.0.1:3306", help="hmonitor database host")
define("mysql_database", default="hmonitor", help="hmonitor database name")
define("mysql_user", default="root", help="hmonitor database user")
define("mysql_password", default="rootroot", help="hmonitor database password")
#Zabbix
define("zabbix_user", default="Admin", help="Zabbix user name")
define("zabbix_password", default="zabbix", help="Zabbix password")
define("zabbix_url", default="http://127.0.0.1/zabbix", help="Zabbix URL")


def main():
    db = HMonitorDB(mysql_user=options.mysql_user,
                    mysql_passwd=options.mysql_password,
                    mysql_host=options.mysql_host,
                    mysql_database=options.mysql_database)
    zabbix = ZabbixProxy(username=options.zabbix_user,
                         password=options.zabbix_password,
                         url=options.zabbix_url)
    triggers = zabbix.get_triggers()
    db.clear_hm_triggers()
    
    for trigger in triggers:
        logging.info("CREATE TRIGGER: {t}".format(t=trigger["description"]))
        db.create_hm_triggers(trigger["description"],
                              trigger["priority"],
                              trigger["comments"])


if __name__ == "__main__":
    main()
