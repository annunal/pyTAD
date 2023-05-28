# pyTAD
Python version of tad programme for IDSLs, by Alessandro Annunziato, Joint Research Centre
(c)  2022

The programmes in the prog folder represent the suite of programmes used in the Inexpensive Device for Sea Level Measurements ( IDSLs) devices and whose objective is to process the data in real time to provide an alert in case an anomalous wave, originated by a Tsunami or any other reason, is detected. 

The programme to be run on the IDSL can be launched with the command:

<code>
  python3 tad.py [ -c  <path of the configuration file>]
</code>

  
however for testing purposes, it is possible to use the scrape.py programme to read the sea level from available sea level repositories and get the quantities calculated on the fly.

To test the calculation procedure you can use the following command:
  
 Suppose that you have to analyse the tide gauge from the GLOSS Sea Level Facility,  you can use this command below, using as parameter  code  the value of the code from this list:
  https://www.ioc-sealevelmonitoring.org/list.php 
  
  If you want to analyse Ierapetra, in Greece, the code is <b>iera</b>.  Any available signal in the list above can be used.
  
  <code>
   python3 scrape.py -code  iera  -n300 200  -n30 50  -mult 4  -add 0.1  -th 0.08 -mode GLOSS -sensors rad -out ./temp/iera
  </code>
  
  where:
  <table>
    <tr><td>parameter</td><td>Meaning</td></tr>
    <tr><td>-code</td><td>is the code of the device,  as from the list indicated above</td></tr>    
    <tr><td>-n300</td><td>the long term number of intervals; the lenght depends on the interval among two points in the dataset</td></tr>    
    <tr><td>-n30</td><td>the short term number of intervals; the lenght depends on the interval among two points in the dataset</td></tr>    
    <tr><td>-mult</td><td>rms multiplication factor</td></tr>    
    <tr><td>-add</td><td>is the adding quantity to the rms</td></tr>    
    <tr><td>-add</td><td>is the adding quantity to the rms</td></tr>    
    <tr><td>-th</td><td>threshold  to be overpassed</td></tr>    
    <tr><td>-mode</td><td>type of sea level netwrok  (GLOSS/NOAA, BIG_INA...)</td></tr>        
    <tr><td>-out</td><td>optional and indicates where to write the output</td></tr>            
    <tr><td>-sensors</td><td>optional except for GLOSS. In the case of GLOSS you need to specify which sensor is to be read, comma separated. For example  rad,enc</td></tr> 
  </table>
  
The output will be in the form of a list of data analysed applying the detection algorithm.  If the command is repeated, only the new data will be considered from the last time the command was run.  The response is the following 
  
  ![image](https://user-images.githubusercontent.com/10267112/172593612-b56043eb-2e96-420f-aafd-52ea1da71518.png)

  The quantities in the middle represent the se alevel,  the foreacsat short term and forecast long term
  
  iera,08/06/2022,00:10:00,0.0,0.0,**0.237,0.241,0.238**,0.00250,0.002,0,0.00,,,
  
  The quantities displayed are generated according to thsi definition:
  logData='$IDdevice,$DATE,$TIME**,$TEMP,$PRESS,**$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL**,$V1,$V2,$V3,
**  
  Temp, PRESS and V1, V2 and V3 are not relevant and always kep contact. The quantities in bold are the ones considered/
  
  The plot of these quantities is the following:
  
  ![image](https://user-images.githubusercontent.com/10267112/172593417-7a97ba45-50f3-4ccb-af62-54f346ef1837.png)
  
  If you would like to analyse one of the nOAA sea levels according to the list of sea levels  contained in this page:
  https://tidesandcurrents.noaa.gov/sltrends/sltrends_us.html
  
  then clicking on  one specific area, i.e. Oregon:
  https://tidesandcurrents.noaa.gov/sltrends/sltrends_states.html?gid=1234
  
  the number appearing as station ID is what is needed.  So  for Charleston, is :  **9435380**
  
  So to analyse this you should call:
  
<code>
  python3 scrape.py -code  9435380  -n300 100  -n30 20  -mult 4  -add 0.1  -th 0.08 -mode NOAA  -out /tmp/Charleston
</code>
  
  ![image](https://user-images.githubusercontent.com/10267112/172599427-39374fb1-7caf-487c-832d-21520faf8996.png)

You can note that the long term forecast does not well follow the level signal. The reson is that the number of points chosen, 100 is too large because this signal has only one point every 6 minutes. Therefore 100 points represent 10h  that is too much.  The maximum should be in the oreder of 2h  and therefore the n300 value should be around 20.  The short term forecast n30 should be 2 or 3.  This procedure works well with a rather dense number of points, not so coarse as in thsis case


The SeaLevelMachine is the software contained in the test application: https://slm.azurewebsites.com   that allows to perform calculations on the fly of a huge amount of sea level stations and verify the effect of changing the parameters.  The application is very primitive but is done only to test the routine and show how they can be implemented in other programs.

![image](https://user-images.githubusercontent.com/10267112/187837319-18f264eb-8103-4c76-b0e5-690a20e37bc0.png)
