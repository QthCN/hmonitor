import logging

from hmonitor.handlers import BaseHandler

class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        self.set_secure_cookie("mail", self.get_argument("mail"))
        self.redirect("/")

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("mail")
        self.render("login.html")