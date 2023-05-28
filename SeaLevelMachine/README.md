![image](https://user-images.githubusercontent.com/10267112/193202256-f86499b5-a709-408f-93fe-e5022eb5634f.png)

## Introduction
The Seal Level Machine is a web site that visualizes all the Tsunami events occurred since year 2000.  The data are obtained from the NOAA NGDC database (https://www.ngdc.noaa.gov/hazard/tsu_db.shtml). For each event the correspondibng report in the Global Disaster Alerts and Coordination System (GDACS, http://www.gdacs.org) is identified and connected.  This allows to extract the GTS message that were produced by the Tsunami Service Providers for that particular event, that are stored in the GDACS database.  

GDACS developed routines to extract from each GTS message the reported Tsunami height, period and arrival time.  This allows therefore to visualize for each event which tide gauge was used by the Tsunami Service Providers during their analysis and if possible,  download and process these data.

Unfortunately not for all the events we have the GTS messages. GDACS started to collect them routiney since 2014 and with the help of some colleagues from NOA, Athens, we could include some data from 2012 to 2014. Also, in some cases the GTS mesages are not visible either because they are not open but protected by a passowrd (i.e. Australian Metereological Bureau) or because the processing of the GTS does not allow a secure understanding.

From the events that do not have GTS messages assciated,  we attempted to identify the gauges in teh area closeby the event (at a distance linearly increasing with magnitude). For these tide gauges, if the signals were available we processed with the Tsunami Detection model described in the pyTAD branch of this gitHub system and if we identified an 'alert' we marked that tide gauge useful for that particular event. With such methodology we could detect alerts in about half the events. Nevertheless, in some cases, the alert is not due to the tsunami wave but spurious spikes in the signals. This cannot be avoided and should require manual moderation that, for the moment was not done.

## Example of list of events
![image](https://user-images.githubusercontent.com/10267112/193110688-b72dbb44-f395-4742-a388-67812352aee4.png)
The figure above shows the map of all the events from 2000 to current date.  The list shows the events separated by year. A filter allows to make a selection based on Minimum Magnitide or Minimum measured height (reported in the GTS messages (see above),  the starting/ending year of the list or the presence or absence of GTS message.

## When a GTS message is present for an event...
By clicking on one of the events (for example Mexico Sept 2022), a new page is loaded,  showing the characteriscs of the event and the list of measures present for each event, as deduced from al the GTS messages connected with that event.
![image](https://user-images.githubusercontent.com/10267112/193122347-45cb4001-a702-4fbb-a7ce-516df0fe674b.png)

By clicking on one of the tide gauge,  if data are (still) available in any of the available databases,,  the behaviour of the sea level is presented, together with a number of additional curves obtained with the Tsunami detection  model.
![image](https://user-images.githubusercontent.com/10267112/193121210-95ead093-678d-4d95-a1fb-fb3079c923bd.png)

Another useful curve shown is also the power spectrum of the signal whcih allowd to understand which could be the best parameters to apply to the signal.

A number of dropdown menu allows to modify the model arameters and by clicking the 'Get Data'button, it alows to donload and process the data according to the selected model. It is possible to get a link that identify this signal with the selected parameters (or future reference)  or download the data with the specific button.
![image](https://user-images.githubusercontent.com/10267112/193121831-03a3aaed-2b9f-4801-b067-10e73846d87c.png)

### In case a GTS message is not present ?
For the events for which a GTS message is unavailable, was not collected or was difficult or impossible to extract its content or no measurement was present in that particualr GTS message,  it is still possible to visulize the sea levels of the gauges closby.  By default a distance is calculated as a function of the magnitude but it is possible to extend this distance using a filter  The system will show all the tide gauges according to the default or the selected distance. 

It is not sure that a Tsunami is visible at these tide gauges. However the system will show, marking the with "DET.  # gauges: xx" showing how many tide gauges have a signal that showed an alert. This will facilitate the selection of a signal showing an event.  However still it is not 100% sure that a Tsunami is visible at that location because the alert could be due to a siganl spike that was not eliminated with the procedure.

For example,  selecting the Honshu event of Japan, 2011,  for which no GTS was available, the system shows several red dots  and in the list they are identified as *DETECTED* for signals that have tested positive to the Tsunami dtection model.
![image](https://user-images.githubusercontent.com/10267112/193124250-82bfc1b6-dcc4-4b03-b884-4c8b523faf65.png)

In this case a filter section allows to establish the maximum distance to search events, the database name to use or a search keyowrd to find a specific tide gauge.

### Determination of Tsunami parameters
Once you show a level signal, it is possible to easily identify the parameters that characterize a measurement point, that are:
- Arrival time
- Maximum Amplitude (m)
- Wave Period (minutes)

In order to do that, you need to click 5 times on a curve
![points](https://user-images.githubusercontent.com/10267112/193201525-972f0e1e-8fb5-4d1c-b13c-ba76e3704e9a.jpg)

- click #1 to identify the **Arrival time**
- click #2 on a zero at the start of a cycle corresponding to the largest cycle
- click #3 on a maximum (or a minimum) of the same cycle
- click #4 on a minimum (or a naximum) of the same cycle
- click #5 on a zero at the end of the same cycle

The results is the following, displayed on the screen:

- Time of Maximum: **2022-09-19 19:05**
- Amplitude: **0.9 m** *(half trough to crest)*
- Period: **33 min**
-Other info
- Arrival Time:  2022-09-19 18:28:0
- Max Amplitude: 1.0 m  *(max between trough and crest minus tide)*
- Through to Crest: 1.7 m 
- 

the data in bold are generally the relevant data to be used by Tsunami Service providers. The other information are for statistical purpose. 

In principle through experts analysis of each of the identified signals, these information could be stored in a database and presented together with the other for events that have the GTS messages associated. 

