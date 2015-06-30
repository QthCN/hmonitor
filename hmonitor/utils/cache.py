# -*- coding: utf-8 -*-

import datetime


cache_dict = dict()


def get_cached_content(key):
    v = cache_dict.get(key, None)
    if v is None:
        return None
    if (datetime.datetime.now() - v["added_time"]).seconds > v["cache_time"]:
        return None
    else:
        return v["value"]


def set_cached_content(key, value, cache_time=300):
    cache_dict[key] = dict(added_time=datetime.datetime.now(),
                           value=value,
                           cache_time=cache_time)
