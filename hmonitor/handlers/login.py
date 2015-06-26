import logging

from hmonitor.handlers import BaseHandler


class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        mail = self.get_argument("mail")
        password = self.get_argument("password")

        if self.db.check_password_by_mail(mail, password):
            self.set_secure_cookie("mail", mail)
            self.redirect("/")
        else:
            logging.warn("INVALID AUTH INFO: mail: {m}, password: {p}".format(
                m=mail,
                p=password
            ))
            self.render("403.html")

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("mail")
        self.render("login.html")

