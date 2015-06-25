import logging

#TODO(tianhuan) Add cache expire feature

cache_dict = dict()

def get_cached_content(key):
    return cache_dict.get(key, None)

def set_cached_content(key, value):
    cache_dict[key] = value