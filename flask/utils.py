import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config
import pytoml

ENV_FILE = config.ENV_FILE # path to dir in which we will save ids
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


# mail_server = None

@singleton
class MailService:
    def __init__(self):
        self.MAIL_SERVER_HOST = config.MAIL_SERVER_HOST
        self.MAIL_SERVER_PORT = config.MAIL_SERVER_PORT
        self.MAIL_SERVER_LOGIN = config.MAIL_SERVER_LOGIN
        self.MAIL_SERVER_PASSWORD = config.MAIL_SERVER_PASSWORD
        self.FROM_EMAIL = config.FROM_EMAIL
        if not self.FROM_EMAIL:
                self.FROM_EMAIL = 'admin@alerta.aydo.com'

        if not self.MAIL_SERVER_HOST:
            raise Exception('MAIL SERVER HOST IS NOT SET')
        self.server =smtplib.SMTP(self.MAIL_SERVER_HOST, self.MAIL_SERVER_PORT)
        if self.MAIL_SERVER_LOGIN and self.MAIL_SERVER_PASSWORD:
            self.server.log(self.MAIL_SERVER_LOGIN, self.MAIL_SERVER_PASSWORD)

    def send(self, to, body):
        msg = MIMEMultipart()
        msg['subject'] = "New Alert"
        msg['from'] = self.FROM_EMAIL
        msg['to'] = to
        body = MIMEText(body, 'html')
        msg.attach(body)
        self.server.sendmail(self.FROM_EMAIL, to, msg.as_string())

def body_as_html(text):
    html = """\
<html>
<head></head>
<body>
<p>Hi!<br>
   There is a new alert for you <br/>
   {}
</p>
</body>
</html>
        """.format(text)
    return html

def construct_message_text(data):
    text = '[%s](%s) %s: %s - %s on %s\n%s' % (
    data['short_id'],
    '%s/#/alert/%s' % (config.ALERTA_DASHBOARD_URL, data['id']),
    data['environment'],
    data['severity'],
    data['event'],
    data['resource'],
    data['text']
    )
    return text

def get_envs():
    envs = {}
    with open (ENV_FILE, "rb") as f:
        envs = pytoml.load(f)
    return envs
