# -*- coding: utf-8 -*-

import abc

import six
from stevedore import driver


EXECUTOR_NAMESPACE = "hmonitor.utils.executor"


@six.add_metaclass(abc.ABCMeta)
class ExecutorBase(object):

    def __init__(self, hostname, user):
        self.hostname = hostname
        self.user = user

    @abc.abstractmethod
    def execute(self, cmd):
        pass


def get_executor(driver_name):
    mgr = driver.DriverManager(
        namespace=EXECUTOR_NAMESPACE,
        name=driver_name,
        invoke_on_load=False,
    )
    return mgr.driver
