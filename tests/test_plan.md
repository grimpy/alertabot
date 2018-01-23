## Manual test scenarios : 

### Scenario 1 ("check that alerta doesn't have fake alerts")
- Get random error or warnning alert,and get the following parameters from error :(Environment(En1), category, text and service).
- Check that the Environment(En1) has this Error or warnning with right category, text and service . 

### Scenario 2 ("Check that the  new error or warnning in healthchek in ovc will reflect in alerta")
- Try to generate Error in health check as example stress one of cpu load to level which make error appear in System Load healthcheck
- Check that this Error appear too in alerta with proper parameters (Environment, category, text and service)
- reduce the load from  cpu and make sure that healthcheck error ended , check it closed too in alerta . 

### Scenario 3 ( "Check sending message with error or warnning on telegram") 
- Check that any warnning or Error in alerta, will be sent to ops telegeram chat . 
- Check that any warnning or Error in alerta, will be sent to someone who responsible of monitoring  as exist in ops spreedsheet .
- Check if monitor ack the message ,nothing happen but Error or warrnig will be exist in alerta unless the problem solved. 
- Check if monitor didn't ack the message for 15 min , the message will be sended to on-call one.
- Check if on-call one  didn't ack the message for 15 min , the message will be sended to on-call two.


### Scenario 4 ( Check that there is no any duplicated events )
