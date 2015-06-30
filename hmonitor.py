import os

import tornado
import tornado.httpserver
from tornado.options import define, options

from hmonitor.autofix import load_autofix_scripts
from hmonitor.handlers.events import (MyEventsHandler,
                                      AllEventsHandler)
from hmonitor.handlers.alert import AlertHandler
from hmonitor.handlers.alerts import (MySubscribeAlertsHandler,
                                      SubscribeAlertsHandler,
                                      AlertsStatHandler)
from hmonitor.handlers.login import LoginHandler, LogoutHandler


define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="hmonitor database host")
define("mysql_database", default="hmonitor", help="hmonitor database name")
define("mysql_user", default="root", help="hmonitor database user")
define("mysql_password", default="rootroot", help="hmonitor database password")
define("zabbix_user", default="Admin", help="Zabbix user name")
define("zabbix_password", default="zabbix", help="Zabbix password")
define("zabbix_url", default="http://127.0.0.1/zabbix", help="Zabbix URL")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MyEventsHandler),
            (r"/index.html", MyEventsHandler),
            (r"/myevents.html", MyEventsHandler),
            (r"/allevents.html", AllEventsHandler),

            (r"/mysubscribealerts.html", MySubscribeAlertsHandler),
            (r"/subscribealerts.html", SubscribeAlertsHandler),
            (r"/alertsstat.html", AlertsStatHandler),

            (r"/alert", AlertHandler),

            (r"/login.html", LoginHandler),
            (r"/logout.html", LogoutHandler),
        ]
        settings = dict(
            blog_title="Monitor",
            template_path=os.path.join(os.path.dirname(__file__),
                                       "hmonitor",
                                       "templates"),
            static_path=os.path.join(os.path.dirname(__file__),
                                     "hmonitor",
                                     "static"),
            debug=True,
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login.html",
        )
        super(Application, self).__init__(handlers, **settings)
        load_autofix_scripts()


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
