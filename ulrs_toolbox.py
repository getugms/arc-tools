#import arcpy
import requests
import time
import xml.etree.ElementTree as etree


## Take inputs from the ESRI toolbox for the client and the address to geocoded - 20130705 - james
#inaddress   = arcpy.GetParameterAsText(0)
#inclient  = arcpy.GetParameterAsText(1)


## Use requests and the inputs to pass the HTTP request - 20130705 - james
#payload = {'street': '1 Brown St', 'f': 'json'}
payload2 = {'clientname': 'james', 'input': '1 brown st'}
#req = requests.get("http://192.168.104.82/ULRSv3/rest/services/Locators/Address_Philadelphia/GeocodeServer/findAddressCandidates", params=payload)
req2 = requests.get("http://geoweb.phila.gov/geospatial.webservices/GISService.asmx/Geocode", params=payload2)

## Testing - james
#print req2.url
#print req2.text


## Writes the HTTP repsonse to a file, the service returns XML - 20130705 - james
file1 = open('response.xml', 'w')
file1.write(req2.text)
file1.close()

  
## ElementTree parses the XML for the XCoord and YCoord values and assigns them to variables  - 20130705 - james
file1 = open('response.xml', 'r')
tree = etree.parse('response.xml')
root = tree.getroot()	

xcoord = root[1][0][1].text
ycoord = root[1][0][2].text
coord = xcoord + ',' + ycoord + '\n'

## The coordinates are appended/written? to a csv file - 20130705 - james
file2 = open('geocoord.csv', 'a')
file2.write(coord)

## Testing - james
# print x
# print y
# time.sleep(5)

## Close all the files - 20130705 - james
file1.close()
file2.close()
