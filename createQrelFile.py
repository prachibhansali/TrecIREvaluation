#!/usr/bin/python

import urllib2
import json
import simplejson

url = "http://localhost:9200/ap_dataset/document/_search?size=600"
res=urllib2.urlopen(url)
parsed_json = json.loads(res.read())
print parsed_json
hits = parsed_json['hits']['hits']

f = open("qrel",'w')

for hit in hits:
	j = hit['_source']
	f.write(str(j['queryid'])+"\tprachi\t"+j['id'].encode('utf-8')+"\t"+str(j['grade'])+"\n")

