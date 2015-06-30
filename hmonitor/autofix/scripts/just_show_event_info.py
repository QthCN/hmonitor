# -*- coding: utf-8 -*-
from hmonitor.autofix.scripts import AutoFixBase


class JustShowEventInfo(AutoFixBase):

    def do_fix(self, event):
        print "in JustShowEventInfo"

    def get_author(self):
        return "Qin TianHuan"

    def get_version(self):
        return "1"

    def get_description(self):
        return u"测试用脚本"

    def get_create_date(self):
        return "2015-06-30 09:00:00"