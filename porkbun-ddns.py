import json
import requests
import re
import sys
from ipaddress import ip_address

def getRecords(domain): #grab all the records so we know which ones to delete to make room for our record. Also checks to make sure we've got the right domain
	allRecords=json.loads(requests.post(apiConfig["endpoint"] + '/dns/retrieve/' + domain, data = json.dumps(apiConfig)).text)
	if allRecords["status"]=="ERROR":
		print('Error getting domain. Check to make sure you specified the correct domain, and that API access has been switched on for this domain.');
		sys.exit();
	return(allRecords)
	
def getMyIP():
	ping = json.loads(requests.post(apiConfig["endpoint"] + '/ping/', data = json.dumps(apiConfig)).text)
	return(ping["yourIp"])

def deleteRecord():
	for i in getRecords(rootDomain)["records"]:
		if i["name"]==fqdn and (i["type"] == 'A' or i["type"] == 'AAAA' or i["type"] == 'ALIAS' or i["type"] == 'CNAME'):
			print("Deleting existing " + i["type"] + " Record")
			deleteRecord = json.loads(requests.post(apiConfig["endpoint"] + '/dns/delete/' + rootDomain + '/' + i["id"], data = json.dumps(apiConfig)).text)

def createRecord(version: int = 6):
	createObj = apiConfig.copy()
	if version == 6:
		createObj["endpoint"] = "https://porkbun.com/api/json/v3"
	else:
		createObj["endpoint"] = "https://api-ipv4.porkbun.com/api/json/v3"
	createObj.update({ 'name': subDomain, 'type': 'AAAA' if version == 6 else 'A', 'content': myIP, 'ttl': 300 })
	endpoint = apiConfig["endpoint"] + '/dns/create/' + rootDomain
	print("Creating record: " + fqdn + " with answer of " + myIP)
	create = json.loads(requests.post(apiConfig["endpoint"] + '/dns/create/'+ rootDomain, data = json.dumps(createObj)).text)
	return(create)

if len(sys.argv)>2: #at least the config and root domain is specified
	apiConfig = json.load(open(sys.argv[1])) #load the config file into a variable
	rootDomain=sys.argv[2].lower()
		
	if len(sys.argv)>3 and sys.argv[3]!='-i': #check if a subdomain was specified as the third argument
		subDomain=sys.argv[3].lower()
		fqdn=subDomain + "." + rootDomain
	else:
		subDomain=''
		fqdn=rootDomain

	if len(sys.argv)>4 and sys.argv[3]=='-i': #check if IP is manually specified. There's probably a more-elegant way to do this
		myIP=sys.argv[4]
	elif len(sys.argv)>5 and sys.argv[4]=='-i':
		myIP=sys.argv[5]
	else:
		myIP=getMyIP() #otherwise use the detected exterior IP address

	deleteRecord()
	print(createRecord(ip_address(myIP).version)["status"])
	
else:
	print("Porkbun Dynamic DNS client, Python Edition\n\nError: not enough arguments. Examples:\npython porkbun-ddns.py /path/to/config.json example.com\npython porkbun-ddns.py /path/to/config.json example.com www\npython porkbun-ddns.py /path/to/config.json example.com '*'\npython porkbun-ddns.py /path/to/config.json example.com -i 10.0.0.1\n")
