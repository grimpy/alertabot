
# Installing alerta
you can follow these steps to install Alerta as described [here](https://github.com/gigforks/alerta/blob/master/docs/Installation.md)
# Installing GIG plugins
from inside `alertabot/alerta_plugin/` folder do
```
pip3 install .
```
modify `/etc/alertad.conf ` to add the gig plugin
```
PLUGINS=['gig']
FLASK_API_URL="http://localhost:5000/alerts"
```
also you can define new alerts severity like this
```
SEVERITY_MAP = {
    'fatal': 0,
    'critical': 1,
    'warning': 4,
    'indeterminate': 5,
    'ok': 5,
    'unknown': 9
}
```

# Starting Flask Server
copy config.example under alertabot/flask to config.py and edit it to have the following information
```
TOKEN = "<Bot Token>" # The token you got from the bot father after creating the bot
MESSAGE_TIMEOUT = 30 # Define the period in which an agnet can reply to the message before escalations (in seconds)
PULL_REPO_PERIOD = 1800 # Define when you want to schedule a repo pull (in seconds)
CHAT_IDS_PATH = "/opt/chat_ids.toml" # A path to TOML file to store chat_ids in
REPO_URL = "ssh://git@docs.greenitglobe.com:10022/gig/gig_team.git" # git url for the teams repo your key should be authorized first
REPO_PATH = "/opt/code/docs.greenitglobe.com/gig/gig_team" # path to where you want to put the code in
ALERTA_DASHBOARD_URL = "<Alerta_url>" # ex. alerta.gig.con
ALERTA_API_URL = "<alerta_api>" # ex. alerta.gig.com/api
ALERTA_API_KEY = "<ALERTA_KEY>" # you can generate one from alerta portal
ENV_FILE = "/opt/code/docs.greenitglobe.com/gig/gig_team/teams/operations/env.toml"
MAIL_SERVER_HOST = "localhost"
MAIL_SERVER_PORT = ""
MAIL_SERVER_LOGIN = ""
MAIL_SERVER_PASSWORD = ""
FROM_EMAIL = "admin@alerta.aydo.com"
GOOGLE_API_KEY_PATH="/opt/code/key1.json"
AGENTS_SHEET_NAME="NOC and On-Call Shift Schedule"
DEVOPS_SHEET_NAME = "DevOps"
MONITORS_SHEET_NAME = "NOC Monitoring"
SHIFTS_CODE_NAME = "Shifts"
```
to get `GOOGLE_API_KEY_PATH` follow [this](http://gspread.readthedocs.io/en/latest/oauth2.html)
make sure you did this step
```
Go to Google Sheets and share your spreadsheet with an email you have in your json_key['client_email']. Otherwise you’ll get a SpreadsheetNotFound exception when trying to open it.
```

to export spread sheet to toml. configuring a cron job is required to do this every month
```
crontab -e
```
this will open an editor where you can add the job

```
0 0  1   *   *     python3 /opt/code/github/openvcloud/alertabot/flask/cron.py >/dev/null 2>&1
```
