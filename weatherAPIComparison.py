import requests, pprint, datetime

headers = {'Accept':'application/json'}

def printWeather (pKey,x, level):
    formatDict = {'dt':'date','sunrise':'time','sunset':'time','moonrise':'time','moonset':'time','moon_phase':'float', 'day':'temp', 'min':'temp', 'max':'temp', 'night':'temp', 'eve':'temp', 'morn':'temp','pressure':'int','humidity':'float','dew_point':'float','wind_speed':'float','wind_deg':'int','wind_gust':'float', 'main': 'str', 'description': 'str', 'clouds':'int','rain':'float' ,'uvi':'float'}
    for k in x.keys():
        # is this a single k/v pair or a dict?
        if isinstance(x[k],list):
            for e in x[k]:
                printWeather(pKey+k+':',e, level+1)
        elif isinstance(x[k],dict):
            printWeather(pKey+k+':',x[k], level+1)
        else:
            if k in formatDict:
                fmtType = formatDict[k]
                if fmtType == 'time':
                    print (pKey+k,':',datetime.datetime.fromtimestamp(x[k]).strftime("%H:%M"),sep='',end=' ')
                elif fmtType == 'date':
                    print (datetime.datetime.fromtimestamp(x[k]).strftime("%y-%m-%d"),sep='',end=' ')
                elif  fmtType == 'temp':
                    print (pKey+k,':',x[k],'C',sep='',end=' ')
                else: # Everything else
                    print (pKey+k,':',x[k],sep='',end=' ')
    if level == 0:
        print('')


citySearchURL = "https://api.openweathermap.org/geo/1.0/direct?limit=1&appid=6da4b00ffc971ffaa637108dfa22c622&"
PCSearchURL = 'http://api.openweathermap.org/geo/1.0/zip?appid=6da4b00ffc971ffaa637108dfa22c622&'
reverseLocURL = 'http://api.openweathermap.org/geo/1.0/reverse?limit=10&appid=6da4b00ffc971ffaa637108dfa22c622&'
weatherFetchURL = "http://api.openweathermap.org/data/2.5/onecall?exclude=minutely,hourly&units=metric&appid=6da4b00ffc971ffaa637108dfa22c622&"
weatherIconURL = "http://openweathermap.org/img/wn/***@2x.png"

owBaseUrl = 'http://api.openweathermap.org/data/2.5/onecall?exclude=minutely,hourly&units=metric&appid=6da4b00ffc971ffaa637108dfa22c622&'
#owBaseUrl = 'http://api.openweathermap.org/data/2.5/weather?appid=6da4b00ffc971ffaa637108dfa22c622&&units=metric&'
cityPlaceHolder = 'xxxxxx'
owCity = 'q='+cityPlaceHolder
zipPlaceHolder = 'zzzzzz'
ccPlaceHolder = 'yy'
owPostcode = 'zip='+zipPlaceHolder+','+ccPlaceHolder

location = 'Reading'
postCode = 'RG30 6AF'
country = 'GB'


# get current location first - by City
r=requests.get(citySearchURL+'q=Reading', headers = headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'])
cityLocation = r.json()
#pprint.pprint(cityLocation)

# get location by postCode
r=requests.get(PCSearchURL+ owPostcode.replace(zipPlaceHolder,postCode).replace(ccPlaceHolder,country), headers = headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'] )
PCLocation = r.json()
#pprint.pprint(PCLocation)

latLonQuery = 'lat='+str(PCLocation['lat'])+'&lon='+str(PCLocation['lon'])
print (latLonQuery)
# Do a reverse lookup!
r=requests.get(reverseLocURL+latLonQuery, headers = headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'] )
revLocation = r.json()
#pprint.pprint(revLocation)
for x in revLocation:
    print(x['country']+":"+x['local_names']['feature_name']+':lat='+str(x['lat'])+':lon='+str(x['lon']))

url = owBaseUrl + latLonQuery
#print (url)
r=requests.get(url, headers = headers)
print ('Result',r.status_code)
#print ('Type', r.headers['content-type'])
dailyData = r.json()
#pprint.pprint(dailyData)
for x in dailyData['daily']:
    dateT = datetime.datetime.fromtimestamp(x['dt'])
    print (dateT.strftime('%a'), end=' ')
    printWeather('',x,0)
    
url = owBaseUrl + owPostcode.replace(zipPlaceHolder,postCode).replace(ccPlaceHolder,country)
#print (url)
#r=requests.get(url, headers = headers)
#print ('Result',r.status_code)
#print ('Type', r.headers['content-type'])
#jsonData = r.json()
#pprint.pprint(jsonData)
