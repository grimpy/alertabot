# Alerta bot
## when an alert is sent to alerta the plugin will send this to the app which will do the following
* Send a telegram message to all monitors on shift
* If they didn't reply Send to the OC-1 (on call devops)
* If they didn't reply Send to the OC-2 (on call devops) backup
* send telegram message to the on-call devops. if he didn't reply sends to its back up, if the backup didn't reply it sends to the person that they both reports_into
*Monitors and devops data will come from this [google spread sheet](https://docs.google.com/spreadsheets/d/1tEIk3hQ2P5edrhste73WF8hTtNDfWOatpcCYuwUlPmE)

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
