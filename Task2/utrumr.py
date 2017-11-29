
from __future__ import division
import os
import json
import csv
import ast
import operator
import csv
from scipy.stats import spearmanr

# test words for which we need UTR
# this can be modified for our use
words = []
with open("230Words.txt","r") as infile:
	for line in infile :
		words.append(line.strip())

#utr
tweet_hindi = {}
tweet_cmh = {}
tweet_english = {}

for word in words:
	tweet_hindi[word] = 0
	tweet_english[word] = 0
	tweet_cmh[word] = 0

with open("final.json","r") as infile:
	dct = json.load(infile)

count=0
errorCount = 0
st=""
TweetTag = {}
with open('Datasheet.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',')
	for row in spamreader:
		count+=1
		print count
		id=str(row[0])
		try :
			tweet = dct[id]
		except :
			errorCount+=1
			continue
		check = {}
		check["HI"] = 0
		check["EN"] = 0
		for item in row[1:] :
			items = item.split(":")
			start = int(items[0])-1
			end = int(items[1])
			lang = items[2]
			if lang == "HI" : check[lang]+=1
			elif lang == "EN" : check[lang]+=1

		length = check["HI"] + check["EN"]
		if check["HI"]/(length) >= 0.9 : TweetTag[id] = "HI"
		elif check["EN"]/(length) >= 0.9 : TweetTag[id] = "EN"
		elif check["HI"]/(length) >= 0.5 and check["HI"] > check["EN"] : TweetTag[id] = "CML"
		else : TweetTag[id] = "NIL"

hi=0
en=0
NIL=0
CML=0
for key,value in TweetTag.items() :
	if value=="HI" : hi+=1
	elif value=="EN" : en+=1
	elif value=="CML" : CML+=1
	elif value=="NIL" : NIL+=1

print hi,en,CML,NIL

utr_dict={}
count=0
with open("230Words.txt","r") as infile :
	for word in infile :
		word = word.strip()
		count+=1
		print count,word
		l1 = 0
		l2 = 0
		cml = 0
		utr=0.0
		for key, value in TweetTag.items() :
			tweet = dct[key]
			tweet = tweet.strip().replace("."," ")
			tweet = tweet.replace("!"," ")
			tweet = tweet.replace(","," ")
			lst = [wrd.encode('UTF-8') for wrd in tweet.split()]
			if word in lst and value != "NIL":
				if value == "HI" : l1+=1
				elif value == "EN" : l2+=1
				else : cml+=1 

		if l2 > 0 : utr = (l1+cml)/l2
		utr_dict[word] = utr
		print l1,l2,cml

with open("utr_dict1.json","w") as out:
	json.dump(utr_dict,out)
utr_dict = json.load(open("utr_dict1.json"))
print utr_dict
d_view = [ (v,k) for k,v in utr_dict.iteritems() ]
d_view.sort(reverse=True) # natively sort tuples by first element
f1 = open("Ranked230Words.txt","w")
for v,k in d_view:
    f1.write(k+"\n")
    print "%s: %d" % (k,v)

f = open("groundTruths.txt")

i = 1
groundTruths = {}
for line in f:
	groundTruths[line.strip()] = i
	i+=1

metricRanks = {}
i = 1
for utr, word in d_view:
	word = word.strip()
	if len(word) == 0:
		continue
	if word in groundTruths:
		metricRanks[word] = i
		i+=1


print spearmanr(metricRanks.values(), groundTruths.values())

