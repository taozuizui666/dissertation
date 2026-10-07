import numpy as np
import os
from glob import glob
from os.path import basename
from sklearn.ensemble import RandomForestClassifier
from micromlgen import port

folder = 'dataset'

def load_features(folder):
    dataset = None
    classmap = {}
    for class_idx, filename in  enumerate(glob('%s/*.txt' % folder)):
        class_name = basename(filename)[:-4]
        classmap[class_idx] = class_name
        samples = np.loadtxt(filename,dtype=float,delimiter=',')
        lables = np.ones((len(samples),1))*class_idx
        samples = np.hstack((samples,lables))
        dataset = samples if dataset is None else np.vstack((dataset,samples))
    return dataset,classmap

def get_classifier(features):
    X,y = features[:,:-1],features[:,-1]
    return RandomForestClassifier(20,max_depth=10).fit(X=X,y=y)


if __name__ == '__main__':
    features,classmap = load_features(folder=folder)
    classifier = get_classifier(features=features)
    c_code = port(clf= classifier, classmap=classmap)
    with open("model.h",'w') as f:
        f.write(c_code)
        f.close()
    