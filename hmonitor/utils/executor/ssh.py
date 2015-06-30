# -*- coding: utf-8 -*-

import logging
import subprocess

from hmonitor.utils.executor import ExecutorBase


class SSHExecutor(ExecutorBase):

    def __init__(self, hostname, user):
        super(SSHExecutor, self).__init__(hostname, user)
        self.command_prefix = "ssh {u}@{h} ".format(u=self.user,
                                                    h=self.hostname)

    def get_cmd(self, cmd):
        return "{p} '{c}'".format(p=self.command_prefix, c=cmd)

    def execute(self, cmd):
        logging.debug("EXECUTE CMD: {c} AS USER: {u}".format(c=cmd,
                                                             u=self.user))
        cmd = self.get_cmd(cmd=cmd)
        try:
            output = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            logging.exception(e)
            return False, None
        return True, output

