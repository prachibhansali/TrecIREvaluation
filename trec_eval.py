#!/usr/bin/python

from collections import defaultdict

print "Start Evaluation";

#qrel_loc = "qrels.adhoc.51-100.AP89.txt"
#rankedlist_loc = "okapiBM25.txt"

precisions = defaultdict(list)
recall = defaultdict(list)
kprecisions = defaultdict(list)
krecall = defaultdict(list)
fValues = defaultdict(list)
avgPrecisions = {}
rPrecisions = {}
grades = defaultdict(list)
ndcg = {}
kranks = [5,10,20,50,100]

queryRelevantDocs = defaultdict(list)
rankedDocs = defaultdict(list)



def computePrecisionsAndRecall():
	for key, value in rankedDocs.items():
		rel=0
		qlen = len(queryRelevantDocs[key])
		fl = open(str(key),'w')
		for index, docid in enumerate(value):
			if(docid in queryRelevantDocs[key]):
				rel=rel+1
			precision_index=float(rel)/(index+1)
			recall_index=float(rel)/qlen
			if(docid in queryRelevantDocs[key]):
				precisions[key].append(precision_index)
				recall[key].append(recall_index)
				fl.write(str(recall_index)+"\t"+str(precision_index)+"\n")
			if((index+1) in kranks):
				kprecisions[key].append((index+1,precision_index))
				krecall[key].append((index+1,recall_index))
				fval = computeFValue(precision_index , recall_index)
				fValues[key].append((index+1,fval))
			if((index+1)==len(queryRelevantDocs[key])):
				rPrecisions[key]=precision_index
	return

def computeAveragePrecision():
	for key,value in precisions.items():
		sum=0
		for f in value:
			sum = sum + float(f)
		sum = sum/(len(queryRelevantDocs[key]))
		avgPrecisions[key]=sum
	return

def computeFValue(p,r):
	if(p==0 and r==0):
		return 0
	return (2*float(p)*float(r))/(float(p)+float(r))

import math
def computeNDCG():
	for key,value in rankedDocs.items():
		sum=0
		for index,docid in enumerate(value):
			if(docid in queryRelevantDocs[key]):
				rank = index+1;
				ids = [id for id in grades[key] if id[0] == docid]
				tup = ids[0]
				grade = tup[1]
				sum = sum + (((2**grade)-1) * (1/(math.log((1+rank),2))))
		ndcg[key] = sum
	return

def computeKAverageAllQueries(lst):
	kp = []
	for rank in kranks:
		sum=0
		for key,values in lst.items():
			scores = [score for score in values if score[0]==rank]
			for score in (item[1] for item in scores):
				sum = sum + score
		sum = sum/(len(lst))
		kp.append(sum)
	#print len(lst)
	return kp

def computeAverageAllQueries(lst):
	avg=0
	for _,v in lst.items():
		avg = avg+v	
	return float(avg)/len(avgPrecisions)

def evaluate(hasQ,qrel_loc,rankedlist_loc):
	with open(qrel_loc) as f:
		for line in f:
			(qid,_,docid,rel) = line.split('\t')
			if(int(rel)==1 or int(rel)==2):
				queryRelevantDocs[int(qid)].append(docid)
				grades[int(qid)].append((docid,int(rel)))
	#print len(queryRelevantDocs)

	with open(rankedlist_loc) as r:
		for line in r:
			print line
			(qid,_,docid,_,score,_) = line.split('\t')
			t=(docid,float(score))
			rankedDocs[int(qid)].append(t)

	import operator
	for qid, value in rankedDocs.items():
		value.sort(key=operator.itemgetter(1),reverse=True)
		rankedDocs[qid]=list(x[0] for x in value)
	#print rankedDocs

	computePrecisionsAndRecall()
	computeAveragePrecision()

	# for k,v in kprecisions.items():
	# 	print k
	# 	print v

	# for k,v in avgPrecisions.items():
	# 	print k
	# 	print v

	# for k,v in rPrecisions.items():
	# 	print k
	# 	print v

	# for k,v in fValues.items():
	# 	print k
	# 	print v

	computeNDCG()
	# for k,v in ndcg.items():
	# 	print k
	# 	print v

	if(hasQ==True):
		avgPrecisionAllQueries = computeAverageAllQueries(avgPrecisions)
		avgRPrecisionAllQueries = computeAverageAllQueries(rPrecisions)
		avgndcgAllQueries = computeAverageAllQueries(ndcg)
		(rt,rl,retrel,pvd,rvd,fvd) = writeEvaluation("TrecEvalOutput")
	writeAverageOverQueries(rt,rl,retrel,pvd,rvd,fvd,avgPrecisionAllQueries,avgRPrecisionAllQueries,avgndcgAllQueries,"TrecEvalOutput")
	#print computeKAverageAllQueries(kprecisions)
	#print computeKAverageAllQueries(krecall)
	#print computeKAverageAllQueries(fValues)
	return

def writeEvaluation(filename):
	print "Writing"
	retrievedDocs=0
	relevantDocs=0
	retrel = 0
	pvd = {}
	rvd = {}
	fvd = {}
	
	f=open(filename,'a')
	for q in avgPrecisions:
		f.write('Query ID :  '+ str(q) + '\n')
		f.write('Total number of documents \n')
		f.write('Retrieved : '+str(len(rankedDocs[q])) + '\n')
		retrievedDocs = retrievedDocs + len(rankedDocs[q])
		f.write('Relevant : '+str(len(queryRelevantDocs[q])) + '\n')
		relevantDocs = relevantDocs + len(queryRelevantDocs[q])
		relev = set(queryRelevantDocs[q])
		retr = set(rankedDocs[q])
		f.write('ret_rel : ' + str(len(relev.intersection(retr))) + '\n')
		retrel = retrel+len(relev.intersection(retr))
		f.write('Average precision (non-interpolated) for all rel docs(averaged over queries)\n')
		f.write('\t\t'+str(avgPrecisions[q])+'\n')
		f.write('Precision: \n')
		f.write('Precision'+'\t\t\t'+'Recall'+'\t\t\t'+'F1'+'\n')
		k=0
		for pv,rv,fv in zip(kprecisions[q],krecall[q],fValues[q]):
			f.write(str(pv)+'\t'+str(rv)+'\t'+str(fv)+'\t'+'\n')
			val = pvd[k] if k in pvd else 0 
			pvd[k]=val+pv[1]
			val = rvd[k] if k in rvd else 0 
			rvd[k]=val+rv[1]
			val = fvd[k] if k in fvd else 0 
			fvd[k]=val+fv[1]
			k=k+1

		f.write('NDCG : '+str(ndcg[q])+'\n')
		f.write('R-Precision (precision after R (= num_rel for a query) docs retrieved):\n')
		f.write('\t\tExact: '+str(rPrecisions[q]) + '\n')
	return (retrievedDocs,relevantDocs,retrel,pvd,rvd,fvd)

def writeAverageOverQueries(rt,rl,retrel,pvd,rvd,fvd,avgPrecisionAllQueries,avgRPrecisionAllQueries,avgndcgAllQueries,filename):
	f=open(filename,'a')
	f.write('Query ID :  25\n')
	f.write('Total number of documents \n')
	f.write('Retrieved : '+str(rt) + '\n')
	f.write('Relevant : '+str(rl) + '\n')
	f.write('ret_rel : ' + str(retrel) + '\n')
	f.write('Average precision (non-interpolated) for all rel docs(averaged over queries)\n')
	f.write('\t\t'+str(avgPrecisionAllQueries)+'\n')
	f.write('Precision: \n')
	f.write('Precision'+'\t\t\t'+'Recall'+'\t\t\t'+'F1'+'\n')
	writeKValues(pvd,rvd,fvd,f)
	f.write('R-Precision (precision after R (= num_rel for a query) docs retrieved):\n')
	f.write('\t\tExact: '+str(avgRPrecisionAllQueries) + '\n')
	f.write('ndcg over all queries :\n')
	f.write('\t\tExact: '+str(avgndcgAllQueries) + '\n')
	return

def writeKValues(pvd,rvd,fvd,f):
	k=0
	length = len(kprecisions)
	print "length"
	print length
	for r in kranks:
		print "writing kv values"
		print pvd[k],rvd[k],fvd[k]
		f.write(str(float(pvd[k])/length)+"\t"+str(float(rvd[k])/length)+"\t"+str(float(fvd[k])/length)+"\t\n")
		k=k+1
	return

import sys
import getopt
def main():
	f=open("TrecEvalOutput",'w')
	hasQ = True
	try:
		opt,args = getopt.getopt(sys.argv[1:],"q",[])
		for option in opt:
			print option
			if(option == '-q'):
				print "has q"
				hasQ=True
		if(len(args)==2) :
			qrel_loc=args[0]
			rankedlist_loc=args[1]
			evaluate(hasQ,qrel_loc,rankedlist_loc)
		else:
			print "Error in number of arguments entered"
	except getopt.GetoptError:
		usage()
		sys.exit(2)

if __name__ == '__main__':
	main()


