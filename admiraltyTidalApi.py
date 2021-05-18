import requests, pprint, datetime, json

url ='https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations'

headers = {'Accept':'application/json', 'Ocp-Apim-Subscription-Key':'apikey'}

coord = [-1.021254233956172,51.45985952778045]

with open('admiralty.key') as f:
    apikey = json.load(f)
    
headers['Ocp-Apim-Subscription-Key'] = apikey['apikey']

r = requests.get(url, headers=headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'])
jsonData = r.json()

# Now look for the station closest to the provided lon/lat
# using a simple metric of the smallest absolute angular deltas
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
# Did we find one?
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
    leadTide = ''
    for x in jsonData:
        dateT = datetime.datetime.fromisoformat(x['DateTime']+'+00:00')
        if x['EventType'] == 'LowWater':
            evT = 'LT'
        else:
            evT = 'HT'
        if leadTide == '':
            leadTide = x['EventType']
        if leadTide != x['EventType']:
            print (evT,' ', dateT.strftime('%X'),' %4.2f' % x['Height'],' ', sep='',end='\n')
        else:
            print (dateT.strftime('%y'), '-',dateT.strftime('%m'),'-',dateT.strftime('%d'), ' ', evT,' ',  dateT.strftime('%X'),' %4.2f' % x['Height'],' ', sep='', end='')

#pprint.pprint(jsonData)
