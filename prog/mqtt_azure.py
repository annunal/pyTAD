import uuid
import asyncio
import os,time
import threading
# pip3 install azure-eventhub
# pip3 install azure-iot
# pip3 install azure-iot-device

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

from azure.eventhub import TransportType
from azure.eventhub.aio import EventHubConsumerClient

from datetime import datetime
_localMsgQueue=[]
_indexNames={}
_config={}

def init_push(config,queueMQTT,adcData,folderOut):
    print ("---------------------------------------------------")
    print ("Starting MQTT AZURE client PUSH")
    print ("using ", config['MQTT_AzureIOTHub_PUSH_conn_str'])
    print ("---------------------------------------------------")
    asyncio.run(push(config,queueMQTT,adcData,folderOut))

async def push(config,queueMQTT,adcData,folderOut):
    global _connected
    print('starting asyncio push')
    #AzureIOTHub_conn_str = "HostName=JRC-Telemetry.azure-devices.net;DeviceId=IDSL-309;SharedAccessKey=vggL/j5H73Lj1XI6qxyDLnllyKCD+3VJEcAj5Q0Wmpc=" #Azure IOT Hub Connection String
    AzureIOTHub_conn_str =config['MQTT_AzureIOTHub_PUSH_conn_str']
    idDevice=config['IDdevice']

    device_client = IoTHubDeviceClient.create_from_connection_string(AzureIOTHub_conn_str)
    
    # Connect the device client.
    await device_client.connect()
    
    t0=datetime.utcnow()    
    _connected=device_client.connected
    print(str(datetime.now()) + " | Async connection established to Azure IOT")
    
    # Send a single message
    print(str(datetime.now()) + " | Starts sending message to Azure IOT Hub")
    
    try:  
          while True: 
            n=0
            print(len(queueMQTT),_connected,device_client.connected)
            while len(queueMQTT)>0: # or (nd>=len(queueData)-1 and nd>ndata):
                  #if (datetime.utcnow()-t0).total_seconds()>3600 and _connected:
                  #    await device_client.disconnect()
                  #    _connected=False

                  #if not _connected:
                  #      print('connecting to MQTT server',_connected)                    
                  #      await device_client.connect()
                  #      
                  #      print('connected',_connected)                    
                  #      _connected=device_client.connected
                  #      t0=datetime.utcnow()
                  #print('before for: ',len(queueMQTT))
                  for j in range(len(queueMQTT)-1):
                      if j<len(queueMQTT):
                        tt,value=queueMQTT[j]
                        queueMQTT.pop(0)
                        PAYLOAD=config['MQTT_msg']
                        PAYLOAD=PAYLOAD.replace('$IDdevice',idDevice)
                        PAYLOAD=PAYLOAD.replace('$DATETIME',format(tt))
                        PAYLOAD=PAYLOAD.replace('$TEMP','%.1f' % float(adcData['tempCPU']))
                        PAYLOAD=PAYLOAD.replace('$PRESS','%.2f' % float(adcData['pressure']))
                        PAYLOAD=PAYLOAD.replace('$LEV',"%.3f" % value)
                        PAYLOAD=PAYLOAD.replace('$BATT','%.2f' % float(adcData['batteryValue']))
                        PAYLOAD=PAYLOAD.replace('$CPUTEMP','%.3f' % float(adcData['tempValue']))
                        PAYLOAD=PAYLOAD.replace('$TEMP380','%.3f' % float(adcData['temperature380']))
                        n+=1
                        if n==20:
                            print(PAYLOAD)
                            n=0
                        try:
                            
                            msg = Message(PAYLOAD)
                            msg.message_id = uuid.uuid4()
                            msg.content_encoding = "utf-8"
                            msg.content_type = "text/html"
                            await device_client.send_message(msg)
                        except:
                            await device_client.disconnect()
                            _connected=False
                            
                        time.sleep(0.05)

            time.sleep(0.1)
    except Exception as e:
            print(e)
            with ('/tmp/stopping_MQTT.txt', 'a') as f:
                  f.write(e)
            os.kill(os.getpid(), 9)        

async def on_event_batch(partition_context, events):
    global _lo_localMsgQueue
    try:
        for event in events:
            PAYLOAD=event.body_as_str()
            #print('Received PYLOAD=',PAYLOAD)
            _localMsgQueue.append(PAYLOAD)
    except Exception as e:
        print(e)
    await partition_context.update_checkpoint()

async def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


    
def Azure_Listen(config,queueData,adcData,queueMQTT,folderOut,proxy='',debug=False):
    #_config=config
    for key in config.keys():
        _config[key]=config[key]
    print ("---------------------------------------------------")    
    print ("Listening Azure MQTT using ", config['MQTT_AzureIOTHub_LISTEN_conn_str'])
    print ("---------------------------------------------------")

    CONNECTION_STR=config['MQTT_AzureIOTHub_LISTEN_conn_str']
    idDevice=config['IDdevice']
    if not 'MQTT_readDevice' in config:
        config['MQTT_readDevice']=idDevice
    PAYLOAD=config['MQTT_msg']

    n=-1

    for f in PAYLOAD.split('|'):
      n+=1
      _indexNames[f.replace('$','')]=n   
    tr =threading.Thread(target=process_data, args=(config,queueData,adcData,queueMQTT,folderOut))
    tr.start()
      
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
        # transport_type=TransportType.AmqpOverWebsocket,  # uncomment it if you want to use web socket
        # http_proxy={  # uncomment if you want to use proxy 
        #     'proxy_hostname': '127.0.0.1',  # proxy hostname.
        #     'proxy_port': 3128,  # proxy port.
        #     'username': '<proxy user name>',
        #     'password': '<proxy password>'
        # }
    )
    
    try:
        loop.run_until_complete(client.receive_batch(on_event_batch=on_event_batch, on_error=on_error))
    except KeyboardInterrupt:
        print("Receiving has stopped.")
    finally:
        loop.run_until_complete(client.close())
        loop.stop()


def process_data(config,queueData,adcData,queueMQTT,folderOut):
    while True:
        try:
            if 'MQTT_model' in _config:
                model=_config['MQTT_model']    
            for j in range(len(_localMsgQueue)):
              if j<len(_localMsgQueue):
                t0=datetime.utcnow()
                PAYLOAD=_localMsgQueue[j]
                _localMsgQueue.pop(0)

                if model=='IDSL':
                    p=PAYLOAD.split('|')
                    if len(p)>1: 
                        tt=datetime.strptime(p[_indexNames['DATETIME']],'%Y-%m-%d %H:%M:%S.%f')
                        queueData.append((tt,float(p[_indexNames['LEV']])))
                        adcData['batteryValue']=p[_indexNames['BATT']]
                        adcData['tempValue']=p[_indexNames['TEMP']]
                        adcData['tempCPU']=p[_indexNames['CPUTEMP']]
                        adcData['pressure']=p[_indexNames['PRESS']]
                        adcData['temperature380']=p[_indexNames['TEMP380']]
                        adcData['SensorLevel']=p[_indexNames['LEV']]
                        fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                   
                        with open(fname,'a') as fh:
                            fh.write(format(tt)+' '+p[_indexNames['LEV']]+'\n')
                elif model=='PUMMA':
                    dd=json.loads(PAYLOAD)
                    DA=dd['UTC_Date']+' '+dd['UTC_TS']
                    lev=float(dd['tinggi'])/100.0
                    #tt=datetime.strptime(DA,'%a %b %d %Y %H:%M:%S')-timedelta(seconds=7*3600)
                    tt=datetime.strptime(DA,'%Y-%m-%d %H:%M:%S')+timedelta(seconds=24*3600)
                
                    queueData.append((tt,lev))
                    if 'tengangan' in dd: adcData['batteryValue']=float(dd['tegangan'])
                    if 'temperature' in dd: adcData['tempValue']=float(dd['temperature'])
                    if 'suhu' in dd: adcData['tempCPU']=float(dd['suhu'])
                    if 'pressure': adcData['pressure']=float(dd['pressure'])
                    adcData['temperature380']=0
                    adcData['SensorLevel']=lev

                        # 'tegangan': 13.4, 'temperature': 32.56, 'humidity': 54.938723240124574, 'pressure': 1009.9360582946874, 'suhu': 44.3}                           
                    fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
               
                    with open(fname,'a') as fh:
                            fh.write(format(tt)+' '+format(lev)+'\n')
             
        except Exception as e:
            print(e)
        time.sleep(0.1)