# -*- coding: utf-8 -*-

import logging
import json
import Queue
import threading

import tornado.httpclient as httpclient
import tornado.httputil as httputil
from tornado.options import options

from hmonitor.autofix import get_autofix_scripts
from hmonitor.common.constants import AUTOFIX_STATUS
from hmonitor.models.db import HMonitorDB
from hmonitor.utils import convert_datetime_to_str
from hmonitor.utils.executor import get_executor


class AutoFixProxy(object):

    def __init__(self, db, executor, url):
        self.db = db
        self.executor_driver_name = executor
        self.executor = get_executor(executor)
        self.autofix_url = url

    def do_fix(self, event):
        """This method will do some checks on the event,
        autofix will be happened only if following checks are passed.

        1. event has an autofix script bound on it
        2. following conditions in 'or':
            a. no autofix logs releated to this event in last 30 minutes
            b. last autofix result is success
            c. last autofix result is fixing or failed,
               but happened in 30 minutes before
            d. last autofix result is fixing, and happened in 5 minutes

        """

        trigger_name = event["trigger_name"]
        hostname = event["hostname"]
        bindings = self.db.get_autofix_bindings()

        for binding in bindings:
            if binding["trigger_name"] == trigger_name:
                break
        else:
            logging.debug("THIS EVENT HAS NO BINDS")
            return False

        autofix_logs = self.db.get_autofix_logs(trigger_name=trigger_name,
                                                hostname=hostname,
                                                last_minutes=30)
        autofix_logs2 = self.db.get_autofix_logs(trigger_name=trigger_name,
                                                 hostname=hostname,
                                                 last_minutes=5)
        if (len(autofix_logs) == 0 or
            autofix_logs[-1]["status"] == AUTOFIX_STATUS["success"] or
            (len([l for l in autofix_logs if l["status"] in (
                AUTOFIX_STATUS["fixing"], AUTOFIX_STATUS["failed"]
            )]) == 0) or
            (len(autofix_logs2) > 0 and
                autofix_logs2[-1]["status"] == AUTOFIX_STATUS["fixing"])):
            return self._send_autofix_request(event)
        else:
            logging.warn("THIS EVENT'S AUTOFIX LOG IS FIXING OR FAILED "
                         "IN LAST 30 MINUTES. IGNORE IT")
            return False

    def _send_autofix_request(self, event):
        body = dict(
            trigger_name=event["trigger_name"],
            hostname=event["hostname"],
            event_id=event["id"],
            event=event["event"],
            value=event["value"],
            type=event["type"],
            last_occur_time=convert_datetime_to_str(
                event["last_occur_time"]
            ),
            first_occur_time=convert_datetime_to_str(
                event["first_occur_time"]
            ),
            severity=event["severity"],
            occur_amount=event["occur_amount"],
            status=event["status"]
        )
        body = json.dumps(body)

        http_request = httpclient.HTTPRequest(url=self.autofix_url,
                                              method="POST",
                                              headers=httputil.HTTPHeaders(
                                                  {"Content-Type":
                                                       "application/json-rpc"}
                                              ),
                                              body=body)
        http_client = httpclient.HTTPClient()
        logging.debug("SEND REQUEST TO HM AUTOFIX: url: {url}, "
                      "body: {body}".format(
            url=self.autofix_url,
            body=body
        ))
        try:
            http_client.fetch(http_request)
        except httpclient.HTTPError as e:
            logging.exception(e)
            return False
        http_client.close()
        logging.debug("REQUEST FINISHED")
        return True


class AutoFixManager(object):

    def __init__(self, worker=8, executor="ssh"):
        self.worker = worker
        self.executor_driver_name = executor
        self.executor = get_executor(executor)
        self.db = HMonitorDB(mysql_user=options.mysql_user,
                             mysql_passwd=options.mysql_password,
                             mysql_host=options.mysql_host,
                             mysql_database=options.mysql_database)

        self.queue = Queue.Queue()

        for w in range(0, self.worker):
            t = threading.Thread(target=self.do_autofix)
            t.daemon = True
            t.start()
        logging.debug("START {0} WORKERS FOR AUTOFIX".format(self.worker))

    def add_task(self, event):
        self.queue.put(event)

    def get_autofix_script(self, trigger_name):
        bindings = self.db.get_autofix_bindings()
        for binding in bindings:
            if binding["trigger_name"] == trigger_name:
                return binding["auto_fix_script"]
        raise RuntimeError("NO SUCH SCRIPT FOR TRIGGER: {t}".format(
            t=trigger_name
        ))

    def do_autofix(self):
        log_id = None
        try:
            event = self.queue.get()
            autofix_script = self.get_autofix_script(event["trigger_name"])
            log_id = self.db.create_autofix_log(
                trigger_name=event["trigger_name"],
                hostname=event["hostname"],
                script=autofix_script,
                event_id=event["event_id"]
            )
            if log_id is None:
                logging.warn("AUTOFIX ALREADY IN WORKING, IGNORE THIS EVENT.")
            else:
                self._do_autofix(event, autofix_script, log_id)
        except Exception as e:
            logging.exception(e)
            if log_id:
                self.db.update_autofix_log(log_id, AUTOFIX_STATUS["failed"],
                                           str(e))
        else:
            if log_id:
                self.db.update_autofix_log(log_id, AUTOFIX_STATUS["success"],
                                           "")

    def _do_autofix(self, event, autofix_script, log_id):
        trigger_name = event["trigger_name"]
        hostname = event["hostname"]
        executor = self.executor(hostname=hostname, user=options.executor_user)
        autofix_method = get_autofix_scripts().get(autofix_script).get(
            "fix_method"
        )
        # do autofix, if it fix failed, it should raise an exception and
        # upper level codes will catch it then record it into database.
        autofix_method(trigger_name, hostname, executor, event)
