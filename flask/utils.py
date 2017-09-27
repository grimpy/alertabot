import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
        self.MAIL_SERVER_HOST = config.get("MAIL_SERVER_HOST", None)
        self.MAIL_SERVER_PORT = config.get("MAIL_SERVER_PORT", None)
        self.MAIL_SERVER_LOGIN = config.get("MAIL_SERVER_LOGIN". None)
        self.MAIL_SERVER_PASSWORD = condig.get("MAIL_SERVER_PASSWORD", None)
        self.FROM_EMAIL = confg.get('FROM_EMAIL', 'admin@alerta.aydo.com')

        if not MAIL_SERVER_HOST:
            raise Exception('EMAIL SERVER HOST IS NOT SET')
        self.server =smtplib.SMTP(MAIL_SERVER_HOST, MAIL_SERVER_PORT)
        if MAIL_SERVER_LOGIN and MAIL_SERVER_PASSWORD:
            self.server.log(MAIL_SERVER_LOGIN, MAIL_SERVER_PASSWORD)

    def send(self, to, body):
        self.server.sendmail(self.FROM_EMAIL, to, body)
    def alert_as_html(self, alert):
        html = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       There is a new alert for you <br>
       Here is the <a href="https://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
        """


def body_as_html(data):
    text = '[%s](%s) %s: %s - %s on %s<br />%s' % (
            data['short_id'],
            '%s/#/alert/%s' % (config.ALERTA_DASHBOARD_URL, data['id']),
            data['environment'],
            data['severity'],
            data['event'],
            data['resource'],
            data['text']
        )

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
