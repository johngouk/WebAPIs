import requests, pprint
url = 'https://api.beta.ons.gov.uk/v1/datasets'
headers = {'Accept':'application/json'}
r = requests.get(url, headers=headers)
print ('Result',r.status_code)
print ('Type', r.headers['content-type'])
jData = r.json()
#pprint.pprint(jData)
print(jData['count'],' ',len(jData['items']))
for x in jData['items']:
    print(x['title'],': ID :',x['id'], ': LR :',x['links']['latest_version']['href'],x['links']['latest_version']['id'])

metaUrl = jData['items'][15]['links']['latest_version']['href']
r = requests.get(url, headers=headers)
jData = r.json()

