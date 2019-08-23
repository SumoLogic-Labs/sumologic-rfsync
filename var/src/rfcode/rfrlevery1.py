#IP List - Cron to run every hour
import urllib.request

url = 'https://api.recordedfuture.com/v2/ip/risklist?format=csv%2Fsplunk'
token = '1b89670de448468ab765ec7976b2a7a7'

req = urllib.request.Request(url, None, {'X-RFToken': token})
res = urllib.request.urlopen(req)

print("Writing Risklist rf_ip_risklist")
with open("rf_ip_risklist.csv", mode="wb") as rl:
    rl.write(res.read())
print("Finished writing Risklist rf_ip_risklist")
