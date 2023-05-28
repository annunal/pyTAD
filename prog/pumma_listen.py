from paho.mqtt.client import Client
from datetime import datetime as datetime
import random
import time

idDevice='PUMMA-01'
MQTT_server='test.mosquitto.org'
MQTT_username='wildcard'
MQTT_password= ''
_topic='PUMMA_telemetry'

print('MQTT: Listening ',MQTT_server)
client = Client(client_id ='LISTENER_'+idDevice) # "sub-test")
        
client.username_pw_set(username=MQTT_username,password=MQTT_password)


def on_connect(client, userdata, flags, rc):
    print("Connesso con successo")


def on_message(client, userdata, message):
    received_msg = message.payload.decode()
    client_id=client._client_id.decode()
    
    if message.topic == _topic:
        print(received_msg)
    else:
        print('discarded '+received_msg)


client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_server)
client.subscribe(_topic)
        
client.loop_start()


while True:
    print('waiting for data')
    time.sleep(10)