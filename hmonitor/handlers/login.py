import logging

from hmonitor.handlers import BaseHandler

class LoginHandler(BaseHandler):

    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        logging.error(self.get_argument("name"))
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")
