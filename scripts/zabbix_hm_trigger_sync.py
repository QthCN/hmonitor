# -*- coding: utf-8 -*-

import logging
import time

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

define("force", default="no", help="sync all releated tables")


def force_sync(db, zabbix_triggers, hm_triggers):
    removed_triggers = []

    for ht in hm_triggers:
        for zt in zabbix_triggers:
            if zt["description"] == ht["description"]:
                break
        else:
            removed_triggers.append(ht)

    db.clear_hm_triggers()

    for trigger in zabbix_triggers:
        logging.info("CREATE TRIGGER: {t}".format(
            t=trigger["description"]
        ))
        db.create_hm_triggers(trigger["description"],
                              trigger["priority"],
                              trigger["comments"])

    # clear alert subscribe list
        for t in removed_triggers:
            logging.info("REMOVE ALERT SUBSCRIBE RECORD ON {tr}".format(
                tr=t["description"]
            ))
            db.remove_binding_trigger_record(t["description"])


def main():
    db = HMonitorDB(mysql_user=options.mysql_user,
                    mysql_passwd=options.mysql_password,
                    mysql_host=options.mysql_host,
                    mysql_database=options.mysql_database)
    zabbix = ZabbixProxy(username=options.zabbix_user,
                         password=options.zabbix_password,
                         url=options.zabbix_url)
    zabbix_triggers = zabbix.get_triggers()
    hm_triggers = zabbix.get_triggers(db=db)
    if options.force.upper() == "NO":
        db.clear_hm_triggers()

        for trigger in zabbix_triggers:
            logging.info("CREATE TRIGGER: {t}".format(
                t=trigger["description"]
            ))
            db.create_hm_triggers(trigger["description"],
                                  trigger["priority"],
                                  trigger["comments"])
    elif options.force.upper() == "YES":
        logging.warn("RUN SYNC WITH FORCE OPTION, SLEEP 5 SECONDS FOR THINK "
                     "AGAIN.")
        time.sleep(5)
        logging.warn("RUN SYNC WITH FORCE NOW")
        force_sync(db, zabbix_triggers, hm_triggers)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    main()
