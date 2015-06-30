from hmonitor.autofix.scripts import AutoFixBase


class JustShowEventInfo(AutoFixBase):

    def do_fix(self, event):
        print "in JustShowEventInfo"
