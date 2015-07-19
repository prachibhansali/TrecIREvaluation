#!/usr/bin/python

from elasticsearch import Elasticsearch

#query="costa concordia disaster and recovery"
#qid = "152601"
#query="South Korea ferry disaster"
#qid = "152602"
query="Lampedusa migrant shipwreck"
qid = "152603"
es = Elasticsearch()
res = es.search(index="maritime_disaster",doc_type="document", body={"fields": ["_id"],"query": {"match": {"text": query}},"size": 1000})

f = open("MaritimeRankedDocs",'a')
index=0
for hit in res['hits']['hits']:
	index=index+1
	f.write(qid+"\t"+"Q0"+"\t"+hit['_id'].encode('utf-8')+"\t"+str(index)+"\t"+str(hit['_score'])+"\t"+"Exp\n")


