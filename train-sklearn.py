#!/usr/bin/env python3

import sys
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import numpy as np
from joblib import dump


def load_data(data):
	features = []
	labels = []
	for interaction in data:
		interaction = interaction.strip()
		interaction = interaction.split('\t')
		interaction_dict = {feat.split('=')[0]:feat.split('=')[1] for feat in interaction[1:] }
		features.append(interaction_dict)
		labels.append(interaction[0])
	return features, labels


if __name__ == '__main__':

	model_file = sys.argv[1]
	vectorizer_file = sys.argv[2] 	

	train_features, y_train = load_data(sys.stdin)
	y_train = np.asarray(y_train)
	# Make yp_train a list of integers Expected: [0 1 2 3 4], got ['advise' 'effect' 'int' 'mechanism' 'null']
	y_train = [0 if label == 'advise' else 1 if label == 'effect' else 2 if label == 'int' else 3 if label == 'mechanism' else 4 for label in y_train]
	classes = np.unique(y_train)
	v = DictVectorizer()
	X_train = v.fit_transform(train_features)
	#clf = MultinomialNB(alpha=0.01)
	#clf.partial_fit(X_train, y_train, classes)
 
	#clf = LinearSVC(max_iter=10000)
	#clf = RandomForestClassifier(n_estimators=100)
	#clf = XGBClassifier()
	clf = SVC(kernel='rbf', probability=True, C=0.9)
	clf.fit(X_train, y_train)
	
	#Save classifier and DictVectorizer
	dump(clf, model_file) 
	dump(v, vectorizer_file)

	 
