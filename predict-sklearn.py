#!/usr/bin/env python3

import sys
from joblib import dump, load
from sklearn.feature_extraction import DictVectorizer
import numpy as np

def prepare_instances(xseq):
	features = []
	for interaction in xseq:
		token_dict = {feat.split('=')[0]:feat.split('=')[1] for feat in interaction[1:]}
		features.append(token_dict)
	return features


if __name__ == '__main__':

    # load leaned model and DictVectorizer
	model = load(sys.argv[1])
	v  = load(sys.argv[2])
	#bias_null = -float(sys.argv[3]) 
	for line in sys.stdin:
		fields = line.strip('\n').split("\t")
		(sid,e1,e2) = fields[0:3]        
		vectors = v.transform(prepare_instances([fields[4:]]))
		prediction = model.predict_proba(vectors)[0]
		prediction[-1]= prediction[-1] # + bias_null
		#percent = np.max(prediction)
		max_idx = np.argmax(prediction)
		#if percent >= 0.8:
		if max_idx==0:
			prediction="advise"
		elif max_idx == 1:
			prediction = "effect"
		elif max_idx == 2:
			prediction = "int"
		elif max_idx == 3:
			prediction = "mechanism"
		elif max_idx == 4:
			prediction = "null"
		#else:
			#prediction="null"
		if prediction != "null" :            
			print(sid,e1,e2,prediction,sep="|")

