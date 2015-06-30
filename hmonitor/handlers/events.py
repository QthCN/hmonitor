# -*- coding: utf-8 -*-

import logging

import tornado.web

import hmonitor.common.constants as constants
from hmonitor.handlers import BaseHandler
from hmonitor.utils import sort_events_by_severity


class MyEventsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        current_total_events_amount = 0
        current_my_events_amount = 0
        current_high_important_amount = 0

        user = self.get_user()

        triggers_subscribed = self.db.get_triggers_name_by_user_id(
            user.get("id", -1)
        )

        current_events = sort_events_by_severity(
            self.db.get_trigger_events_in_problem())
        problem_host = []
        for event in current_events:
            trigger_name = event["trigger_name"]
            hostname = event["hostname"]
            severity = event["severity"]
            releated_to_me = trigger_name in triggers_subscribed

            current_total_events_amount += 1
            if releated_to_me:
                current_my_events_amount += 1
            if hostname not in problem_host:
                problem_host.append(hostname)
            if severity in (constants.ZBX_SEVERITY_MAP["Disaster"],
                            constants.ZBX_SEVERITY_MAP["High"]):
                current_high_important_amount += 1
        current_problem_host_amount = len(problem_host)

        self.render(
            "myevents.html",
            current_total_events_amount=current_total_events_amount,
            current_high_important_amount=current_high_important_amount,
            current_my_events_amount=current_my_events_amount,
            current_problem_host_amount=current_problem_host_amount,
            current_events=current_events,
            triggers_subscribed=triggers_subscribed
        )


class AllEventsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.get_user()
        current_events = sort_events_by_severity(
            self.db.get_trigger_events_in_problem()
        )

        self.render(
            "allevents.html",
            current_events=current_events,
        )
