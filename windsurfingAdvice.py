# A prototype for an app that will provide a notification for suitable conditions
# forecast for a specified windsurfing location
# Given a location, as a name or preferably a lon/lat, and the location's compass bearing, it
#     - checks the tide situation over the next 7 days, looking (initially) for the slot HighWater± 2 hours
#     - looks at the weather for the same period, checking the wind speed and direction (cross-on)
#     - for any day which has interesting conditions, it suggests that period
# It uses a JSON configuration file that holds a list of locations, their lon/lat and their compass bearing
# of the form
# [{"locationName":"Hayling","lon":"-0.9812552319641458","lat":'50.78504188911509","bearing":"185"},
#  {"locationName":"WestwardHo","lon":"-4.232240726879152","lat":"51.05830527471508","bearing":"280"}]

import pprint, requests, datetime, json

force4 = 11 # useful windspeed in knots
m_2_k = 1.944 # conversion factor for m/s to knots

class OpenWeather:
    def __init__(self):
        print ('OpenWeather init')
        self.headers = {'Accept':'application/json'}
        with open('openweather.key') as f:
            openKey = json.load(f)
        self.url = 'http://api.openweathermap.org/data/2.5/forecast?units=metric&appid='+openKey['apikey']+'&'
        
    def getLocationForecast(self,lon,lat):
        forecastUrl = self.url + 'lat='+str(lat)+'&lon='+str(lon)
        r = requests.get(forecastUrl, headers=self.headers)
        print ('Result',r.status_code)
        print ('Type', r.headers['content-type'])
        return r.json()
        
        

class Admiralty:
    def __init__(self):
#        print('Admiralty init')
        self.tideUrl ='https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations'
        self.headers = {'Accept':'application/json', 'Ocp-Apim-Subscription-Key':'apikey'}
        with open('admiralty.key') as f:
            tideKey = json.load(f)
        self.headers['Ocp-Apim-Subscription-Key'] = tideKey['apikey']
        r = requests.get(self.tideUrl, headers=self.headers)
#         print ('Result',r.status_code)
#         print ('Type', r.headers['content-type'])
        self.locationList = r.json()

    def findClosestStation (self, lon, lat):
    # Look for the station closest to the provided lon/lat
    # using a simple metric of the smallest absolute angular deltas
        station = {}
        stationList = []
        minLonDiff = 180
        minLatDiff = 90
        i = 0
        for x in self.locationList['features']:
            lonDiff = abs(x['geometry']['coordinates'][0] - lon)
            latDiff = abs(x['geometry']['coordinates'][1] - lat)
            if  lonDiff <= minLonDiff and latDiff <= minLatDiff:
                minLonDiff = lonDiff
                minLatDiff = latDiff
                i = i + 1
#                 print('Id:',x['properties']['Id'],' Name:',x['properties']['Name'],'lonD:',minLonDiff,':latD:',minLatDiff)
                stationList.append(x)
                station = x
#         print ("total ",i)
#         print('lonD:',minLonDiff,':latD:',minLatDiff)
        return station
    
    def getTideInfo (self, station):
        url = self.tideUrl + '/' + station['properties']['Id'] + '/TidalEvents'
#        print ('URL:'+url)
        r = requests.get(url, headers=self.headers)
#    print ('Result',r.status_code)
#    print ('Type', r.headers['content-type'])
        return r.json()
    

with open('locations.json') as f:
    locations = json.load(f)
#pprint.pprint (locations) 


tideInfo = Admiralty()
weatherInfo = OpenWeather()

stations = []
for l in locations:
    l['station'] = tideInfo.findClosestStation(l['lon'],l['lat'])
    l['tideInfo'] = tideInfo.getTideInfo(l['station'])
#     pprint.pprint (l['station'])
# OK, got the tidal data for our locations for the next 6+1 days
# Let's find some HT±n hours slots
    from datetime import timedelta
    startDelta = timedelta (hours = l['HTDelta'])
#    print (startDelta)
    endDelta = timedelta (hours = -l['HTDelta'])
#    print (endDelta)
    HWTimes = []
    for t in l['tideInfo']:
        if t['EventType'] == 'HighWater':
            dateT = datetime.datetime.fromisoformat(t['DateTime']+'+00:00')
            slotEnd = dateT + endDelta
            slotStart = dateT + startDelta
            HWTimes.append([slotEnd,slotStart])
    start = HWTimes[0][1]
    l['tideSlots'] = []
    for i in range(1,len(HWTimes)-1,1):
        end = HWTimes[i][0]
        if (start.hour < end.hour) and (start.hour > 7 or end.hour < 18):
            l['tideSlots'].append({'start':start,'end':end,'windCount':0})
 #           print (start,'>>>',end)
        start = HWTimes[i][1]
    print (len(l['tideSlots']))
    # Right! We now have some possible tide-driven sailing times
    # Let's refine them with some weather and sunrise/sunset times
    forecast = weatherInfo.getLocationForecast(l['lon'],l['lat'])
#    pprint.pprint (forecast)
    l['goodWindList'] = []
    print(l['locationName'],'has',len(forecast['list']),'entries')
    for d in forecast['list']:
        dt = datetime.datetime.fromtimestamp(d['dt'], tz=datetime.timezone(datetime.timedelta(hours=0),name='UTC'))
        print ('ForecastTZ:',dt.strftime('%Z'))
#        print (l['locationName'],dt.strftime('%a'),dt.strftime('%X'),d['main']['temp'],d['wind']['deg'],d['wind']['speed']*m_2_k,d['wind']['gust']*m_2_k)
        if d['wind']['speed']*m_2_k >= force4: # fast enough?
            upper = (l['bearing']+90)%360 
            lower = (l['bearing']+360-90)%360
            if (upper > lower and d['wind']['deg'] >= lower and d['wind']['deg'] <= upper) \
               or (upper < lower and (d['wind']['deg'] >= lower or d['wind']['deg'] <= upper)):
                print(l['locationName'],dt.strftime('%a'),dt.strftime('%X'),'{:4.2f}'.format(d['main']['temp']),'{:4.2f}'.format(d['wind']['speed']*m_2_k), upper, lower, d['wind']['deg'])
                l['goodWindList'].append(d)
    print(l['locationName'],'has',len(l['goodWindList']),'good entries')
    # Match up the good wind slots with the good tide slots :-)
    print ('StarttZ:',l['tideSlots'][0]['start'].strftime('%Z'))
    print ('EndtZ:',l['tideSlots'][0]['end'].strftime('%Z'))
    for s in l['goodWindList']:
        for t in l['tideSlots']:
            ws = datetime.datetime.fromtimestamp(s['dt'])
            if ws >= t['start'] and ws <= t['end']:
                t['windCount'] = t['windCount']+1
    pprint(l['tideSlots'])
