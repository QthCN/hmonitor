import logging

import tornado.web

from hmonitor.handlers import BaseHandler

class MySubscribeAlertsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_user()
        triggers_name = self.db.get_triggers_name_by_user_id(user.get("id",
                                                                      -1))
        self.render("mysubscribealerts.html", triggers_name=triggers_name)

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
