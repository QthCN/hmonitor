import logging
import requests


class SmsProxy(object):

    def __init__(self, username, password, epid, endpoint, charset="gb2312"):
        self.username = username
        self.password = password
        self.epid = epid
        self.charset = charset
        self.endpoint = endpoint

    def send(self, msg, to):
        sms_obj = dict(
            username=self.username,
            password=self.password,
            epid=self.epid,
            phone=to,
            message=msg.encode(self.charset)
        )
        result = requests.post(self.endpoint, data=sms_obj, timeout=20)
        if result.text != '00':
            logging.error("SEND SMS FAILED. MSG: {0}".format(result.text))
            return False
        logging.debug("SEND SMS SUCCESSFUL.")
        return True
