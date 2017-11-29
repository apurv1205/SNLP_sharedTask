from torch.autograd import Variable
from sklearn.metrics.pairwise import cosine_similarity
import torch.nn as nn
import torch.nn.functional as F
import torch
import json
import pickle
import numpy as np
import csv

class TwinMergeModel(nn.Module):
	
	def __init__(self):
		super(TwinMergeModel, self).__init__()
		self.merge_layer1 = nn.Linear(300, 300)
		self.merge_layer2 = nn.Linear(300, 300)
		self.concatenation_layer = nn.Linear(600, 300)
		self.final_fc = nn.Linear(300,300)

	def forward(self, x1, x2):
		x1 = F.leaky_relu(self.merge_layer1(x1))
		x2 = F.leaky_relu(self.merge_layer2(x2))
		x = torch.cat((x1, x2), 0)
		x = F.leaky_relu(self.concatenation_layer(x))
		x = F.leaky_relu(self.final_fc(x))
		return x

model = TwinMergeModel()
model.cuda()

optimizer = torch.optim.Adam(model.parameters(), lr = 1e-3)
criterion = torch.nn.MSELoss()

trainSet = json.load(open("trainSet"))
testSet = json.load(open("testSet"))

vectors = pickle.load(open("vectors_dct.p"))

new_vectors = pickle.load(open("zorse1.p"))

def bestWord(target, source1, source2, predictedY):
	max_x = -1
	best = None
	#print target
	for key in new_vectors[target]:
		#print np.array(new_vectors[target][key]).reshape(1,-1)
		x = cosine_similarity(predictedY.data.cpu().numpy().reshape(1,-1), np.array(new_vectors[target][key]).reshape(1,-1))
		if x>max_x:
			print target, x, best
			max_x = x
			best = key
	return best


X1 = []
X2 = []
Y = []
print "Training..."

for row in trainSet:
	if row[0] in vectors and row[1] in vectors and row[2] in vectors:
		X1.append(Variable(torch.from_numpy(np.array(vectors[row[1]])).float()).cuda())
		X2.append(Variable(torch.from_numpy(np.array(vectors[row[2]])).float()).cuda())
		Y.append(Variable(torch.from_numpy(np.array(vectors[row[0]])).float()).cuda())
		
train_size = len(X1)
epochs = 100
for epoch in range(0, epochs):
	a = []
	print "Epoch : ", epoch+1
	for i in range(train_size):
	    y_pred = model(X1[i], X2[i])
	    loss = criterion(torch.unsqueeze(y_pred.view(-1),0), Y[i])
	    a.append(loss.data[0])
	    optimizer.zero_grad()
	    loss.backward()
	    optimizer.step()
	print np.mean(a)	

print "Trained"

f = open("NeuralOutput.csv", "w")
writer = csv.writer(f)
writer.writerow(["Source1", "Source2","Prediction", "Target"])
correct = 0
print "Testing.."
a = []
for row in testSet:
	if row[0] in vectors and row[1] in vectors and row[2] in vectors:
		X1 = Variable(torch.from_numpy(np.array(vectors[row[1]])).float()).cuda()
		X2 = Variable(torch.from_numpy(np.array(vectors[row[2]])).float()).cuda()
		Y = Variable(torch.from_numpy(np.array(vectors[row[0]])).float()).cuda()
		y_pred = model(X1, X2)
		ans =  bestWord(row[0],row[1], row[2], y_pred)
		if ans.strip() == row[0].strip():
			correct+=1
		writer.writerow([row[1], row[2], ans, row[0]])
		a.append(cosine_similarity(y_pred, np.array(vectors[row[0]]).reshape(1,-1)))

print "Cosine similarity mean = ", np.mean(a)
print correct