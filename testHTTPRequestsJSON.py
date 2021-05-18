import requests, datetime, pprint
from datetime import date

#def printJSON(jsonThing):
#    thingType = type(jsonThing)
    

url = 'https://collection.sciencemuseumgroup.org.uk/objects/co8357002'
headers = {'Accept':'application/json'}
r = requests.get(url, headers=headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'])
jsonData = r.json()

#pprint.pprint(jsonData, width=0)

print (jsonData.get('data').get('attributes').get('description')[1].get('value'))

#print('dict has ', len(data), ' items')
#print ('')
#print ('dict keys: ',data.keys())
#print ('')
#print ('data len: ',len(data.get('data')))
#print ('')
#print (' data[0] keys: ',data.get('data')[0].keys())
#print ('')
#print (' data[0]:attributes keys: ',data.get('data')[0].get('attributes').keys())
#print ('')
#print (' data[0]:type keys: ',data.get('data')[0].get('type').keys())
#print ('')
#print (' data[0]:id keys: ',data.get('data')[0].get('id').keys())
#print ('')
#print (' data[0]:relationships keys: ',data.get('data')[0].get('relationships').keys())
#print ('')
#print (' data[0]:relationships links: ',data.get('data')[0].get('links').keys())

#print ('')
#print ('data[0].attributes.admin items')
#adminItems = data.get('data')[0].get('attributes').items()
#for x in adminItems:
#    print ('')
#    print (x)
    
#print ('')
#print ('data[0].attributes.admin.description list')
#descItems = data.get('data')[0].get('attributes').get('description')
#for x in descItems:
#    print ('')
#    print (x)

#print ('')
#i = 1
#data = jsonData.get('data')
#print ('Data:',data)
#for x in dataList:
#    print (i, 'id:', x.get('id'), 'title:',x.get('attributes').get('summary_title'))
#    i=i+1
