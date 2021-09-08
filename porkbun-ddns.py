import json
import requests
import re
import sys

def getRecords(domain): #grab all the records so we know which ones to delete to make room for our record. Also checks to make sure we've got the right domain
	allRecords=json.loads(requests.post(apiConfig["endpoint"] + '/dns/retrieveByNameType/' + rootDomain + "/A/" + subDomain, data = json.dumps(apiConfig)).text)
	if allRecords["status"]=="ERROR":
		print('Error getting domain. Check to make sure you specified the correct domain, and that API access has been switched on for this domain.');
		sys.exit();
	return(allRecords)
	
def getMyIP():
	ping = json.loads(requests.post(apiConfig["endpoint"] + '/ping/', data = json.dumps(apiConfig)).text)
	return(ping["yourIp"])

def deleteRecord():
	for i in getRecords(rootDomain)["records"]:
		if i["name"]==fqdn and (i["type"] == 'ALIAS' or i["type"] == 'CNAME'):
			print("Deleting existing " + i["type"] + " Record")
			deleteRecord = json.loads(requests.post(apiConfig["endpoint"] + '/dns/delete/' + rootDomain + '/' + i["id"], data = json.dumps(apiConfig)).text)

def createRecord():
	createObj=apiConfig.copy()
	createObj.update({'name': subDomain, 'type': 'A', 'content': myIP, 'ttl': 600})
	endpoint = apiConfig["endpoint"] + '/dns/create/' + rootDomain
	print("Creating record: " + fqdn + " with answer of " + myIP)
	create = json.loads(requests.post(apiConfig["endpoint"] + '/dns/create/'+ rootDomain, data = json.dumps(createObj)).text)
	return(create)
	
def modRecord():
	createObj=apiConfig.copy()
	createObj.update({'content': myIP, 'ttl': 600})
	endpoint = apiConfig["endpoint"] + '/dns/editByNameType/' + rootDomain + '/A/'+ subDomain
	mod = json.loads(requests.post(apiConfig["endpoint"] + '/dns/editByNameType/'+ rootDomain + '/A/'+ subDomain, data = json.dumps(createObj)).text)
	return(mod)

if len(sys.argv)>2: #at least the config and root domain is specified
	apiConfig = json.load(open(sys.argv[1])) #load the config file into a variable
	rootDomain=sys.argv[2]	
		
	if len(sys.argv)>3 and sys.argv[3]!='-i': #check if a subdomain was specified as the third argument
		subDomain=sys.argv[3]
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

	if getRecords(fqdn)["status"]=="ERROR":
		print(createRecord()["status"])
	else:
		modRecord()
		print("Modifying record: " + fqdn + " with answer of " + myIP)
		
else:
	print("Porkbun Dynamic DNS client, Python Edition\n\nError: not enough arguments. Examples:\npython porkbun-ddns.py /path/to/config.json example.com\npython porkbun-ddns.py /path/to/config.json example.com www\npython porkbun-ddns.py /path/to/config.json example.com '*'\npython porkbun-ddns.py /path/to/config.json example.com -i 10.0.0.1\n")