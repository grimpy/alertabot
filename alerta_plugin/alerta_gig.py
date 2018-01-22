from alerta.app import db
from alerta.app.exceptions import RateLimit
from alerta.plugins import PluginBase
from alerta.app import app
import os
TOKEN = app.config.get('TOKEN')
URL = app.config['FLASK_API_URL']
import requests
import json
class GIGAlert(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if alert.status == 'closed':
            return
        if alert.repeat:
            return
        data = {}
        data['id'] = alert.id
        data['short_id'] = alert.get_id(short=True)
        data['severity'] = alert.severity.capitalize()
        data['text'] = alert.text
        data['environment'] = alert.environment
        data['event'] = alert.event
        data['resource'] = alert.resource
        data['service'] = alert.service
        data['state'] = alert.status
        r = requests.post(URL, data=json.dumps(data))
        return

    def status_change(self, alert, status, text):
        return
