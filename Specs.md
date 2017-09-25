# Alerta bot
## when an alert is sent to alerta the plugin will send this to the app which will do the following
* send telegram message to the on-call devops. if he didn't reply sends to its back up, if the backup didn't reply it sends to the person that they both reports_into
* All these data is written in toml file shift.toml in under operation team repo
* the file will looks like
```
[TG_USERNAME]
period = <CRON_SYNTAX_PERIOD>
excludes = <CRON_SYNTAX_PERIOD>
backup = <TG_USERNAME_OF_BACKUP>
reports_into = <TG_USERNAME>
```
* after sending to the on-call it will send a message to the support group
* then it will send an email to the DevOps support  group
* then it will send a telegram message the specific evn group (JV TG)
* then send an email the the specific env email (JV Email)
* the data for the support group and JVs will be in env.toml which will looks like the followin
```
[support]
emails = []
telegram = []

[RU]
emails = []
telegram = []
env = [be-g8-4]
```
