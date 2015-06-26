import json
import logging

import tornado.httpclient as httpclient
import tornado.httputil as httputil

import hmonitor.common.constants as constants
import hmonitor.utils.cache as cache


class ZabbixProxy(object):

    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = self._parse_url(url)

    def do_request(self, body):
        body = json.dumps(body)
        http_request = httpclient.HTTPRequest(url=self.url,
                                              method="POST",
                                              headers=httputil.HTTPHeaders(
                                                  {"Content-Type":
                                                       "application/json-rpc"}
                                              ),
                                              body=body)
        http_client = httpclient.HTTPClient()
        logging.debug("SEND REQUEST TO ZABBIX: url: {url}, body: {body}".format(
            url=self.url,
            body=body
        ))
        try:
            response = http_client.fetch(http_request)
            result = json.loads(response.body)
        except httpclient.HTTPError as e:
            logging.exception(e)
            result = None
        http_client.close()
        logging.debug("REQUEST RESULT IS: {result}".format(result=result))

        if "error" in result:
            logging.error(result["error"])

        return result

    def get_request_id(self):
        return 1

    def get_token(self):
        # TODO(tianhuan) token should be cached here
        method = "user.login"
        request_body = dict(jsonrpc="2.0",
                            method=method,
                            params=dict(user=self.username,
                                        password=self.password),
                            id=self.get_request_id(),
                            auth=None)
        response = self.do_request(request_body)
        return response.get("result", None)

    def get_triggers(self, only_hm=True):
        method = "trigger.get"
        if cache.get_cached_content(method):
            return cache.get_cached_content(method)

        request_body = dict(jsonrpc="2.0",
                            method=method,
                            params=dict(output="extend",
                                        selectFunctions="extend"),
                            id=self.get_request_id(),
                            auth=self.get_token())
        response = self.do_request(request_body)
        triggers = response.get("result", [])

        if only_hm is False:
            result = triggers
        else:
            result = [t for t in triggers if t["description"].upper().startswith(
                constants.TRIGGER_PREFIX
            )]
        cache.set_cached_content(method, result)
        return result

    def _parse_url(self, url):
        if "http" in url.lower():
            return "{url}/api_jsonrpc.php".format(url=url)
        else:
            return "http://{url}/api_jsonrpc.php".format(url=url)

