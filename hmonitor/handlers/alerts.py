# -*- coding: utf-8 -*-

import logging

import tornado.web
import tornado.httpclient

from hmonitor.handlers import BaseHandler
from hmonitor.utils import convert_str_to_datetime

class MySubscribeAlertsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_user()
        triggers_info = self.zabbix.get_triggers_info(db=self.db)
        triggers_subscribed = self.db.get_triggers_name_by_user_id(
            user.get("id", -1)
        )
        self.render("mysubscribealerts.html", triggers_info=triggers_info,
                    triggers_subscribed=triggers_subscribed)


class SubscribeAlertsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        def convert_list_to_dict(ls):
            d = dict()
            for l in ls:
                name = l["trigger_name"]
                d[name] = l
            return d
        user = self.get_user()
        triggers_info = self.zabbix.get_triggers_info(db=self.db)
        triggers_subscribed = self.db.get_triggers_name_by_user_id(
            user.get("id", -1)
        )
        autofix_bindings = convert_list_to_dict(
            self.db.get_autofix_bindings()
        )
        self.render("subscribealerts.html", triggers_info=triggers_info,
                    triggers_subscribed=triggers_subscribed,
                    autofix_bindings=autofix_bindings)

    @tornado.web.authenticated
    def post(self):
        action = self.request.arguments.get("action")[0]
        trigger_name = self.request.arguments.get("name")[0]
        user = self.get_user()
        logging.debug("User {u} {a} {t}".format(u=user["name"],
                                                a=action,
                                                t=trigger_name))
        try:
            if action == "subscribe":
                self.db.bind_triggers_with_user_id(user_id=user["id"],
                                                   trigger_name=trigger_name)
            else:
                self.db.unbind_triggers_with_user_id(user_id=user["id"],
                                                     trigger_name=trigger_name)
        except Exception as e:
            logging.exception(e)
            # TODO(tianhuan) Use another code here?
            raise tornado.httpclient.HTTPError(400)


class AlertsStatHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        def _get_cataloged_alert_msg(alerts):
            mail_amount = 0
            sms_amount = 0
            for alert in alerts:
                m = alert.get("mail", "")
                p = alert.get("phone", "")
                if m and m != "":
                    mail_amount += 1
                if p and p != "":
                    sms_amount += 1
            return dict(mail=mail_amount, sms=sms_amount)

        user = self.get_user()
        alerts_in_7_days = self.db.get_last_7_days_alert_msgs(
            mail=user["mail"],
            phone=user["phone"]
        )
        alerts_in_30_days = self.db.get_last_30_days_alert_msgs(
            mail=user["mail"],
            phone=user["phone"]
        )

        alerts_in_7_days_stat = _get_cataloged_alert_msg(
            alerts_in_7_days
        )
        alerts_in_30_days_stat = _get_cataloged_alert_msg(
            alerts_in_30_days
        )

        sms_alerts_in_7_days = alerts_in_7_days_stat["sms"]
        mail_alerts_in_7_days = alerts_in_7_days_stat["mail"]
        sms_alerts_in_30_days = alerts_in_30_days_stat["sms"]
        mail_alerts_in_30_days = alerts_in_30_days_stat["mail"]

        self.render("alertsstat.html",
                    sms_alerts_in_7_days=sms_alerts_in_7_days,
                    mail_alerts_in_7_days=mail_alerts_in_7_days,
                    sms_alerts_in_30_days=sms_alerts_in_30_days,
                    mail_alerts_in_30_days=mail_alerts_in_30_days)


class AlertFilterHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        alert_filters = self.db.get_active_alert_filters()
        self.render("alertfilter.html", alert_filters=alert_filters)

    @tornado.web.authenticated
    def post(self):
        action = self.request.arguments.get("action")[0]
        if action == "add":
            trigger_name = self.request.arguments.get("trigger_name")[0]
            hostname = self.request.arguments.get("hostname")[0]
            begin_time = self.request.arguments.get("begin_time")[0]
            end_time = self.request.arguments.get("end_time")[0]
            comment = self.request.arguments.get("comment")[0]
            user = self.get_user()
            username = user["name"]

            try:
                begin_time = convert_str_to_datetime(begin_time)
                end_time = convert_str_to_datetime(end_time)
                self.db.create_alert_filter(trigger_name, hostname, username,
                                            begin_time, end_time, comment)
            except Exception as e:
                logging.exception(e)
                # TODO(tianhuan) Use another code here?
                raise tornado.httpclient.HTTPError(400)
        else:
            trigger_name = self.request.arguments.get("trigger_name")[0]
            hostname = self.request.arguments.get("hostname")[0]
            self.db.cancel_alert_filter(trigger_name, hostname)
