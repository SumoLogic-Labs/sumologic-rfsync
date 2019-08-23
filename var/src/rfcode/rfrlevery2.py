#URL & Domain Lists - Cron to run every other hour
import urllib.request

#Proxy section if needed
#proxy = urllib.request.ProxyHandler({'http': r'http://username:password@url:port'})
#auth = urllib.request.HTTPBasicAuthHandler()
#opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
#urllib.request.install_opener(opener)

url0 = 'https://api.recordedfuture.com/v2/domain/risklist?format=csv%2Fsplunk'
url1 = 'https://api.recordedfuture.com/v2/url/risklist?format=csv%2Fsplunk'
token = '[API_TOKEN_HERE]'


req0 = urllib.request.Request(url0, None, {'X-RFToken': token})
res0 = urllib.request.urlopen(req0)

print("Writing Risklist rf_domain_risklist")
with open("rf_domain_risklist.csv", mode="wb") as rl0:
    rl0.write(res0.read())
print("Finished writing Risklist rf_domain_risklist")

req1 = urllib.request.Request(url1, None, {'X-RFToken': token})
res1 = urllib.request.urlopen(req1)

print("Writing Risklist rf_url_risklist")
with open("rf_url_risklist.csv", mode="wb") as rl1:
    rl1.write(res1.read())
print("Finished writing Risklist rf_url_risklist")