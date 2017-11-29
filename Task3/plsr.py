import json
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np
import gensim
import csv

trainSet = json.load(open("trainSet"))
testSet = json.load(open("testSet"))

vectors = pickle.load(open("vectors_dct.p"))
#print vectors["accenture"]

X = []
Y = []
print "Training..."
for row in trainSet:
	X.append(np.concatenate([vectors[row[1]], vectors[row[2]]]))
	Y.append(vectors[row[0]])


model = PLSRegression(n_components=15,max_iter=10000)
model.fit(X,Y)
print "Trained"

new_vectors = pickle.load(open("zorse1.p"))

def bestWord(target, source1, source2, predictedY):
	max_x = -1
	best = None
	for key in new_vectors[target]:
		x = cosine_similarity(predictedY, np.array(new_vectors[target][key]).reshape(1,-1))
		if x>max_x:
			max_x = x
			best = key
	return best

def bestKWords(target, source1, source2, predictedY,k=5):
	cos_dct={}
	for key in new_vectors[target]:
		x = cosine_similarity(predictedY, np.array(new_vectors[target][key]).reshape(1,-1))
		cos_dct[key] = float(x)

	lst = []
	for key,value in sorted(cos_dct.iteritems(), key=lambda (k,v): (v,k),reverse=True)[:k] :
		lst.append(key)
	return lst

count=0
f = open("Output_pslr.csv", "wb")
writer = csv.writer(f)
writer.writerow(["Source1", "Source2","Prediction", "Target"])
correct = 0
print "Testing..."
testX = []
testY = []
a = []
for row in testSet:
	testX.append(np.concatenate([vectors[row[1]], vectors[row[2]]]))
	testY.append(vectors[row[0]])

	predictedY = model.predict(np.concatenate([vectors[row[1]], vectors[row[2]]]).reshape(1,-1))
	a.append(cosine_similarity(predictedY, np.array(vectors[row[0]]).reshape(1,-1)))
	# ans =  bestWord(row[0],row[1], row[2], predictedY)
	# if ans.strip() == row[0].strip():
	# 	correct+=1
	# writer.writerow([row[1], row[2], ans, row[0]])
	ans_lst =  bestKWords(row[0],row[1], row[2], predictedY,1)
	flg=False
	for ans in ans_lst :
		if ans.strip() == row[0].strip():
			correct+=1
			flg=True
			writer.writerow([row[1], row[2], ans, row[0]])
			break

	if flg == False :
		writer.writerow([row[1], row[2], ans_lst, row[0]])


print "Correctly predicted : ",correct,", Out of :",len(testSet)," test data (last 20 percent of the given dataset)"
print "Mean cosine similarity with predicted vector",np.mean(a)
print "Model score : ",model.score(testX, testY)