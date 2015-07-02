# -*- coding: utf-8 -*-

import logging

import tornado.web
import tornado.httpclient

from hmonitor.handlers import BaseHandler

class AccoundPasswordHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("accountupdatepassword.html")

    @tornado.web.authenticated
    def post(self):
        old_password = self.request.arguments.get("old_password")[0]
        new_password = self.request.arguments.get("new_password")[0]
        user = self.get_user()
        username = user["name"]
        logging.info("User {u} try to update password".format(u=username))
        if self.db.check_password_by_name(username, old_password) is False:
            logging.error("OLD_PASSWOD IS WRONG.")
            raise tornado.httpclient.HTTPError(403)

        self.db.update_password(username, new_password)