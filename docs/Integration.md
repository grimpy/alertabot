# How to integrate alerta with openvcloud
the only thing you should do is add the following 2 lines to `/opt/jumpscale7/hrd/system/system.hrd`

```
alerta.api_key                 = '<API KEY>'
alerta.api_url                 = '<API URL>'

```