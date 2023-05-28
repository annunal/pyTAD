from paho.mqtt.client import Client
from datetime import datetime as datetime
import random
import time

idDevice='PUMMA-01'
MQTT_server='test.mosquitto.org'
MQTT_username='wildcard'
MQTT_password= ''
_topic='PUMMA_telemetry'

client=Client(client_id=idDevice)
client.username_pw_set(username=MQTT_username,password=MQTT_password)
client.connect(MQTT_server)


print('Subscribing to topic ', _topic)
client.subscribe(_topic)
        
while True: 
   # supose that you read the level somewhere 
   #  time and level
   tt=datetime.utcnow()
   lev=random.random()*2.0
   PAYLOAD=format(tt)+','+ '%.3f' %lev
   print(PAYLOAD)
   client.publish(topic=_topic,payload=PAYLOAD)

   time.sleep(0.5)  # this is part pf the reading loop