# -*- coding: utf-8 -*-

import datetime
import json
import os

import hmonitor.common.constants as constants


def sort_events_by_severity(events):
    sorted_events = []
    critical_events = []
    major_events = []
    minor_events = []
    warning_events = []
    information_events = []
    unknown_events = []

    for event in events:
        severity = event["severity"]
        if severity == constants.ZBX_SEVERITY_MAP["Disaster"]:
            critical_events.append(event)
        elif severity == constants.ZBX_SEVERITY_MAP["High"]:
            major_events.append(event)
        elif severity == constants.ZBX_SEVERITY_MAP["Average"]:
            minor_events.append(event)
        elif severity == constants.ZBX_SEVERITY_MAP["Warning"]:
            warning_events.append(event)
        elif severity == constants.ZBX_SEVERITY_MAP["Information"]:
            information_events.append(event)
        else:
            unknown_events.append(event)

    sorted_events.extend(critical_events)
    sorted_events.extend(major_events)
    sorted_events.extend(warning_events)
    sorted_events.extend(minor_events)
    sorted_events.extend(information_events)
    sorted_events.extend(unknown_events)

    return sorted_events

def is_in_working_time(t):
    weekday = t.weekday()
    if weekday in (5, 6):
        return False
    hour = t.hour
    if not (hour >= 10 and hour <= 19):
        return False
    return True

def is_in_working_time_now():
    return is_in_working_time(datetime.datetime.now())

def get_current_file_path(f):
    return os.path.split(os.path.realpath(f))[0]

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

datetime_fmt = "%Y-%m-%d %H:%M:%S"

def convert_datetime_to_str(d):
    return d.strftime(datetime_fmt);

def convert_str_to_datetime(s):
    return datetime.datetime.strptime(s, datetime_fmt)

