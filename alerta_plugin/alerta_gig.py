import logging

from alerta.app import db
from alerta.app.exceptions import RateLimit
from alerta.plugins import PluginBase
from alerta.app import app
import os
LOG = logging.getLogger('alerta.plugins.gig')
import pytoml
TOKEN = app.config.get('TOKEN')
URL = "http://localhost:5000/alerts/"
import requests
import json
class GIGAlert(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):

        data = {}
        data['severity'] = alert.severity
        data['text'] = alert.text
        data['environment'] = alert.environment
        data['status'] = alert.status
        r = requests.post(URL, data=json.dumps(data))
        return

    def status_change(self, alert, status, text):
        return
