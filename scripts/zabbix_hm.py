#!/usr/bin/env python

# Based on https://github.com/alerta/zabbix-alerta

import os
import argparse
import json
import requests

import logging as LOG

__version__ = "0.1.0"

LOG_FILE = "/var/log/zabbix/zabbix_hm.log"
LOG_FORMAT = ("%(asctime)s.%(msecs).03d %(name)s[%(process)d] %(threadName)s "
              "%(levelname)s - %(message)s")
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

ZBX_SEVERITY_MAP = {
    'Disaster':       'critical',
    'High':           'major',
    'Average':        'minor',
    'Warning':        'warning',
    'Information':    'informational',
    'Not classified': 'unknown',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sendto", help="HMonitor API endpoint and key")
    parser.add_argument("summary", help="HMonitor summary")
    parser.add_argument("body", help="HMonitor body")
    args = parser.parse_args()

    LOG.debug("[HMonitor] sendto=%s, summary=%s, body=%s", args.sendto,
              args.summary, args.body)

    if ';' in args.sendto:
        endpoint, key = args.sendto.split(';')
    else:
        endpoint = args.sendto
        key = None

    url = "%s/alert" % endpoint

    alert = dict()
    alert['summary'] = args.summary
    alert['origin'] = 'zabbix/%s' % os.uname()[1]
    alert['rawData'] = args.body

    for line in args.body.split('\n'):
        if '=' not in line:
            continue
        try:
            macro, value = line.split('=', 1)
        except ValueError, e:
            LOG.warning('%s: %s', e, line)
            continue

        if macro == 'service':
            value = value.split(', ')
        if macro == 'severity':
            value = ZBX_SEVERITY_MAP.get(value, 'unknown')
        if macro == 'tags':
            value = value.split(',')
        if macro == 'thresholdInfo':
            macro = 'attributes'
            value = {'thresholdInfo': value}

        alert[macro] = value
        LOG.debug('%s -> %s', macro, value)

    if 'status' in alert:
        if alert['status'] == 'OK':
            alert['severity'] = 'normal'
        del alert['status']

    if 'ack' in alert:
        if alert['ack'] == 'Yes':
            alert['status'] = 'ack'
        del alert['ack']

    LOG.info("[HMonitor] alert=%s", alert)

    headers = {'Content-Type': 'application/json'}
    if key:
        headers['Authorization'] = 'Key ' + key

    try:
        response = requests.post(url, data=json.dumps(alert),
                                 headers=headers, timeout=2)
    except Exception as e:
        LOG.exception(e)
        raise RuntimeError("[HMonitor] Connection error: %s", e)

    LOG.debug('[HMonitor] API response: %s - %s',
              response.status_code, response.json())

if __name__ == "__main__":
    LOG.basicConfig(filename=LOG_FILE, format=LOG_FORMAT,
                    datefmt=LOG_DATE_FMT, level=LOG.DEBUG)
    main()
