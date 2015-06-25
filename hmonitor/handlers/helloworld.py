from hmonitor.handlers import BaseHandler

class HelloWorldHandler(BaseHandler):

    def get(self):
        self.render("helloworld.html")
