RANGE = "10000"
URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'demoevents?limit=' + RANGE
maptarget = f'{URLBASE}/{targetkey}/{URLTAIL}'

headers = {'Content-Type':'txt/plain'}
session = requests.Session()
sumo_category = SRCTAG + '/' + 'demoevents' + '/' + targetkey
headers['X-Sumo-Category'] = sumo_category

req = urllib.request.Request(url, None, {'X-RFToken': APIKEY})
with urllib.request.urlopen(req) as res:
    output = res.read().decode("utf-8")
    with open(targetfile, mode="w", encoding='utf8') as outputfile:
        for line in output.splitlines():
            outputfile.write(line)
            outputfile.write('\n')
    with open(targetfile, mode="r", encoding='utf8') as inputfile:
        rf_map_payload = (inputfile.read().encode('utf-8'))
        postresponse = session.post(SRCURL, rf_map_payload, headers=headers).status_code
