# A prototype for an app that will provide a notification for suitable conditions
# forecast for a specified windsurfing location
# Given a location, as a name or preferably a lon/lat, and the location's compass bearing, it
#     - checks the tide situation over the next 7 days, looking (initially) for the slot HighWater± 2 hours
#     - looks at the weather for the same period, checking the wind speed and direction (cross-on)
#     - for any day which has interesting conditions, it suggests that period
# It uses a JSON configuration file that holds a list of locations, their lon/lat, their compass bearing
# and the useful time after/before HT of the form
# [{"locationName":"Hayling","lon":-1.0066120485105117,"lat":50.78608125774226,"bearing":185, "HTDelta":2},
#  {"locationName":"WestwardHo","lon":-4.232240726879152,"lat":51.05830527471508,"bearing":280, "HTDelta":3},
#  {"locationName":"Christchurch Harbour", "lat":50.724883,"lon":-1.741400, "bearing":100,"LTDelta":3}]
# Possible enhancements:
#   - find some wave forecasts? (hard)
#   - different before/after HT deltas (easy)
#   - sunrise/sunset from forecast combined with slot start/end (not with OpenWeather free 6-day, requires another request
#   - breakfast time inclusion?!
#   - minimum slot time? Sometimes produces slots < 1hr because it's not very smart


import pprint, requests, json
from datetime import timezone, datetime

class OpenWeather:
    def __init__(self):
#        print ('OpenWeather init')
        self.headers = {'Accept':'application/json'}
        with open('openweather.key') as f:
            openKey = json.load(f)
        self.url = 'http://api.openweathermap.org/data/2.5/forecast?units=metric&appid='+openKey['apikey']+'&'
        self.dayUrl = 'https://api.openweathermap.org/data/2.5/onecall?units=metric&exclude=current,minutely,hourly,alerts&appid='+openKey['apikey']+'&'
        
    def getDayInfo(self,lon: float,lat: float) -> dict:
        dayInfoUrl = self.dayUrl + 'lat='+str(lat)+'&lon='+str(lon)
        r = requests.get(dayInfoUrl, headers=self.headers)
# Could do with some error checking!!
#        print ('Result',r.status_code)
#        print ('Type', r.headers['content-type'])
        return r.json()


    def getLocationForecast(self,lon: float,lat: float) -> dict:
        forecastUrl = self.url + 'lat='+str(lat)+'&lon='+str(lon)
        r = requests.get(forecastUrl, headers=self.headers)
# Could do with some error checking!!
#        print ('Result',r.status_code)
#        print ('Type', r.headers['content-type'])
        wInfo = r.json()
        dInfo = self.getDayInfo(lon,lat)
        print(len(wInfo['list']),' items in weather')
        print(len(dInfo['daily']),' items in daily')
        dayInfo = []
        for d in dInfo['daily']:
            times = {'sunrise':d['sunrise'],'sunset':d['sunset']}
            dayInfo.append(times)
        wInfo['daylight'] = dayInfo
        return wInfo
                

class Admiralty:
    def __init__(self):
#        print('Admiralty init')
        self.tideUrl ='https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations'
        self.headers = {'Accept':'application/json', 'Ocp-Apim-Subscription-Key':'apikey'}
        with open('admiralty.key') as f:
            tideKey = json.load(f)
        self.headers['Ocp-Apim-Subscription-Key'] = tideKey['apikey']
        r = requests.get(self.tideUrl, headers=self.headers)
# Could do with some error checking!!
#         print ('Result',r.status_code)
#         print ('Type', r.headers['content-type'])
        self.locationList = r.json()

    def findClosestStation (self, lon: float, lat: float) -> dict:
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
    
    def getTideInfo (self, station: dict) -> dict:
        url = self.tideUrl + '/' + station['properties']['Id'] + '/TidalEvents'
#        print ('URL:'+url)
        r = requests.get(url, headers=self.headers)
# Could do with some error checking!!
#    print ('Result',r.status_code)
#    print ('Type', r.headers['content-type'])
        return r.json()
    
def compass(degrees: int) -> str:
    points = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    slots = [11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75, 191.25, 213.75, 236.25, 258.75, 281.25, 303.75, 326.25, 348.75]
    for i in range(0,len(slots)-1):
        if degrees < slots[i]:
            return points[i]
    return points[0]
    
###################################################
#
#   Main code starts here
#
###################################################

force4 = 11 # useful windspeed in knots
m_2_k = 1.944 # conversion factor for m/s to knots
bearingLimit = 90 # no. degrees +- beach bearing for useful onshore wind


# Load the list of locations and their details

with open('locations.json') as f:
    locations = json.load(f)

# Initialize API classes

tideInfo = Admiralty()
weatherInfo = OpenWeather()

# For each defined location...

for l in locations:
    # Saving the data in the Locations structure...
    # Could in principle combine these into one
    # Was thinking about rewriting config file to include station, as
    # it won't change very often :-), otherwise not used past this point
    l['station'] = tideInfo.findClosestStation(l['lon'],l['lat'])
    l['tideInfo'] = tideInfo.getTideInfo(l['station'])
    

# OK, got the tidal data for our locations for the next 6+1 days
# Let's find some HT±n hours slots
    from datetime import timedelta
    locKeys = l.keys()
    if 'HTDelta' in l.keys():
        # we want HighWater events
        event = 'HighWater'
        key = 'HTDelta'
    elif 'LTDelta' in l.keys():
        # Obviously 'LowWater'
        event = 'LowWater'
        key = 'LTDelta'
    else:
        # explode
        print('Silly arse!! Add HTDelta or LTDelta to your location definition')
        break
    
    startDelta = timedelta (hours = l[key])
    endDelta = timedelta (hours = -l[key])
    HWTimes = []
    for t in l['tideInfo']:
        if t['EventType'] == event:
            dateT = datetime.fromisoformat(t['DateTime']+'+00:00') # Makes it TZ-aware
            slotEnd = dateT + endDelta         # Stop n hours before HT
            slotStart = dateT + startDelta     # Start (again!) n hours after HT
            HWTimes.append([slotEnd,slotStart])

    # Now check the list of HT events for any that are at sensible times
    # Might check sunrise/sunset sometime in the future, from the forecast
    # List is of the form e-HT0-s   e-HT1-s   e-HT2-s
    #   We would sail in these   ^^^       ^^^
    start = HWTimes[0][1]
    l['tideSlots'] = []
    for i in range(1,len(HWTimes)-1,1):
        end = HWTimes[i][0]
        if (start.hour < end.hour) and (start.hour > 7 or end.hour < 18):
            l['tideSlots'].append({'start':start,'end':end,'windCount':0,'forecasts':[]})
        start = HWTimes[i][1]

    # Right! We now have some possible tide-driven sailing times
    # Let's refine them with some weather and sunrise/sunset times
    forecast = weatherInfo.getLocationForecast(l['lon'],l['lat'])
    l['goodWindList'] = []
    for d in forecast['list']:
        dt = datetime.fromtimestamp(d['dt'], tz=timezone.utc)
        if d['wind']['speed']*m_2_k >= force4: # fast enough?
            upper = (l['bearing']+bearingLimit)%360 
            lower = (l['bearing']+360-bearingLimit)%360
            if (upper > lower and d['wind']['deg'] >= lower and d['wind']['deg'] <= upper) \
               or (upper < lower and (d['wind']['deg'] >= lower or d['wind']['deg'] <= upper)):
                l['goodWindList'].append(d)


    # Match up the good wind slots with the good tide slots :-)
    locationHasSlots = False
    for s in l['goodWindList']:
        for t in l['tideSlots']:
            ws = datetime.fromtimestamp(s['dt'],tz=timezone.utc)
            if ws >= t['start'] and ws <= t['end']:
                locationHasSlots = True
                t['forecasts'].append(s)

    # Print stuff out
    if locationHasSlots:
        print(l['locationName']+' sailing opportunities')
        for t in l['tideSlots']:
            if len(t['forecasts']) > 0:
                print('\t'+t['start'].strftime('%d') +' '+t['start'].strftime('%b')+' '+t['start'].strftime('%y')+' '+ t['start'].strftime('%H')+ ':'+ t['start'].strftime('%M')+' --> '+ t['end'].strftime('%H')+ ':'+ t['end'].strftime('%M'))
                for f in t['forecasts']:
                    dt=datetime.fromtimestamp(f['dt'], tz=timezone.utc) 
                    print('\t\t'+dt.strftime('%H')+ ':'+ dt.strftime('%M')+ \
                          ' '+f['weather'][0]['main']+ \
                          ' precip '+'{:3.0f}'.format(f['pop']*100)+'%' + \
                          ' temp '+'{:4.2f}'.format(f['main']['temp'])+ \
                          ' wind '+ compass(f['wind']['deg'])+ \
                              ' spd '+'{:4.2f}'.format(f['wind']['speed']*m_2_k)+ \
                              ' gust '+'{:4.2f}'.format(f['wind']['gust']*m_2_k) \
                          )
#                      ' rain '+str(f['rain']['3h'])+ \ # Turns out 'rain' is optional!
        print(' ')
            

