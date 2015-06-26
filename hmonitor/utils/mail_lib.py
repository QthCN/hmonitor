import logging
import requests


class MailProxy(object):

    def __init__(self, api_user, api_key, sender, endpoint):
        self.api_user = api_user
        self.api_key = api_key
        self.sender = sender
        self.endpoint = endpoint

    def send(self, subject, msg, to):
        mail_obj = dict(
            api_user=self.api_user,
            api_key=self.api_key,
            to=to,
            fromname='HMonitor alerting center',
            subject=subject,
            html=msg
        )
        mail_obj["from"] = self.sender
        result = requests.post(self.endpoint, data=mail_obj, timeout=20)
        if result.json()["message"] != 'success':
            logging.error("SEND MAIL FAILED. MSG: {0}".format(result.text))
            return False
        logging.debug("SEND MAIL SUCCESSFUL.")
        return True
