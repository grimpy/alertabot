
# Installing alerta
you can follow these steps to install Alerta as described [here](http://alerta.readthedocs.io/en/latest/gettingstarted/tutorial-1-deploy-alerta.html#tutorial-1)
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
edit the file `config.py` under alertabot/flask to have the following inf
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
```
