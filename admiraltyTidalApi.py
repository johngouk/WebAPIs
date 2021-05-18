import requests, pprint, datetime

url ='https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations'

headers = {'Accept':'application/json', 'Ocp-Apim-Subscription-Key':'9718c154a61b4c64b156c8ebceb20177'}

coord = [-1.021254233956172,51.45985952778045]

r = requests.get(url, headers=headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'])
jsonData = r.json()
 

#print(len(jsonData))
#print(jsonData.keys())
#print(jsonData['type'],':',len(jsonData['type']),' ',jsonData['features'],':',len(jsonData['features']))

station = {}
stationList = []
minLonDiff = 180
minLatDiff = 90
i = 0
for x in jsonData['features']:
    lonDiff = abs(x['geometry']['coordinates'][0] - coord[0])
    latDiff = abs(x['geometry']['coordinates'][1] - coord[1])
    if  lonDiff <= minLonDiff and latDiff <= minLatDiff:
        minLonDiff = lonDiff
        minLatDiff = latDiff
        i = i + 1
        print('Id:',x['properties']['Id'],' Name:',x['properties']['Name'],'lonD:',minLonDiff,':latD:',minLatDiff)
        stationList.append(x)
        station = x
print ("total ",i)
        
#pprint.pprint(stationList)
#pprint.pprint(station)
print('lonD:',minLonDiff,':latD:',minLatDiff)
if i > 0:
    url = url + '/' + station['properties']['Id'] + '/TidalEvents'
    print ('URL:'+url)
    r = requests.get(url, headers=headers)
#    print ('Result',r.status_code)
#    print ('Type', r.headers['content-type'])
    jsonData = r.json()
#    print(len(jsonData))
#    pprint.pprint(jsonData)
#    print(jsonData[0].keys())
    for x in jsonData:
        dateT = datetime.datetime.fromisoformat(x['DateTime']+'+00:00')
        print (x['EventType'],'\t', dateT,' ',x['Height'],' ',dateT.tzinfo)


#pprint.pprint(jsonData)

