import logging

import tornado.web

from hmonitor.handlers import BaseHandler

class MySubscribeAlertsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_user()
        triggers_info = self.zabbix.get_triggers_info()
        triggers_subscribed = self.db.get_triggers_name_by_user_id(
            user.get("id", -1)
        )
        self.render("mysubscribealerts.html", triggers_info=triggers_info,
                    triggers_subscribed=triggers_subscribed)


class SubscribeAlertsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_user()
        triggers_info = self.zabbix.get_triggers_info()
        triggers_subscribed = self.db.get_triggers_name_by_user_id(
            user.get("id", -1)
        )
        self.render("subscribealerts.html", triggers_info=triggers_info,
                    triggers_subscribed=triggers_subscribed)

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
                if m != "":
                    mail_amount += 1
                if p != "":
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
