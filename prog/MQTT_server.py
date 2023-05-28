#  https://logicaprogrammabile.it/mqtt-installare-mosquitto-raspberry-pi-progetti-iot/
#    install mosquitto-raspberry-pi-progetti-iot/
#      sudo apt-get install mosquitto
#  TEST:
#    mosquitto_sub -h localhost -t "idsl_telemetry"
#    mosquitto_pub -h localhost -t "idsl_telemetry" -m "IDSL test Message"
#    
#  https://antima.it/en/tutorial-using-mqtt-with-python-part-1-the-client-class/
#   install python libraries
#    pip3 install paho-mqtt

from paho.mqtt.client import Client
import time


topic_test1 = "test/1"
topic_test2 = "idsl_telemetry"

last_msg = {}

client = Client(client_id = "sub-test")


def on_connect(client, userdata, flags, rc):
    print("Connesso con successo")


def on_message(client, userdata, message):
    received_msg = message.payload.decode()
    client_id=client._client_id.decode()
    
    if message.topic == topic_test1 or message.topic == topic_test2:
        last_msg[message.topic] = received_msg
    print(received_msg)


client.on_connect = on_connect
client.on_message = on_message

client.connect('localhost')
client.subscribe(topic_test1)
client.subscribe(topic_test2)
client.loop_start()

while True:
    #print(last_msg)
    time.sleep(5)