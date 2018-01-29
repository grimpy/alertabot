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
        db_alert = db.get_alert(alert.id)
        flapping = db.is_flapping(db_alert, 300, 2)
        if flapping:
            return

        data = {}
        data['id'] = alert.id
        data['short_id'] = alert.get_id(short=True)
        data['severity'] = alert.severity.capitalize()
        first_flapping = db.is_flapping(db_alert, 300, 1)
        if first_flapping:
            data['text'] = '{}-(FLAPPING)'.format(alert.text)
        else:
            data['text'] = alert.text
        data['environment'] = alert.environment
        data['event'] = alert.event
        data['resource'] = alert.resource
        data['service'] = alert.service
        data['state'] = alert.status
        r = requests.post(URL, data=json.dumps(data))
        return

    def status_change(self, alert, status, text):
        db_alert = db.get_alert(alert.id)
        flapping = db.is_flapping(db_alert, 300, 2)
        if flapping:
            return
        data = {}
        data['id'] = alert.id
        data['short_id'] = alert.get_id(short=True)
        data['severity'] = alert.severity.capitalize()
        first_flapping = db.is_flapping(db_alert, 300, 1)
        if first_flapping:
            data['text'] = '{}-(FLAPPING)'.format(alert.text)
        else:
            data['text'] = alert.text
        data['environment'] = alert.environment
        data['event'] = alert.event
        data['resource'] = alert.resource
        data['service'] = alert.service
        data['state'] = alert.status
        if status == 'closed':
            r = requests.post('%s/closed' % URL, data=json.dumps(data))
        elif status == 'open':
            r = requests.post(URL, data=json.dumps(data))
        return

