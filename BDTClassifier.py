from sklearn.model_selection import train_test_split
from sklearn.ensemble import *
# from sklearn.preprocessing import normalize
import pandas as pd
import numpy as np
from sklearn.externals import joblib

class BDTClassifier(object):
    def __init__(self, signal):
        self.signal = signal
        self.train_sets = {}
        self.test_sets = {}
        self.features = [
            'mll',
            'mbb',
            'mR',
            'mTR',
            'MET',
            # 'mllbb',
            'THT',
            'ptl1',
            'ptl2',
            'ptb1',
            'ptb2',
            ]

        bgs = ['tt', 'tbW', 'bbWW']
            
        self.get_signal_train_test_data()
        [self.get_bg_train_test_data(bg) for bg in bgs]

        bg_train_sets = [self.train_sets[bg_name] for bg_name in bgs]
        bg_test_sets = [self.test_sets[bg_name] for bg_name in bgs]

        self.X_train = pd.concat([self.train_sets['Signal']]+bg_train_sets)
        self.X_test = pd.concat([self.test_sets['Signal']]+bg_test_sets)

        y_train_signal = [np.ones(self.train_sets['Signal'].shape[0])]
        y_train_bgs = [np.zeros(self.train_sets[bg].shape[0]) for bg in bgs]
        self.y_train = np.concatenate(tuple(y_train_signal+y_train_bgs))

        y_test_signal = [np.ones(self.test_sets['Signal'].shape[0])]
        y_test_bgs = [np.zeros(self.test_sets[bg].shape[0]) for bg in bgs]
        self.y_test = np.concatenate(tuple(y_test_signal+y_test_bgs))

        clf = GradientBoostingClassifier(
                                n_estimators = 1000,
                                learning_rate = 0.025,
                                verbose = 0,
                                )
        clf.fit(self.X_train, self.y_train)
        self.clf = clf

    def get_signal_train_test_data(self):
        df = pd.read_csv('MakeFeatureArrays/Output/'+self.signal.index+'/feature_array.txt',
                        usecols = self.features)
        # df = pd.read_csv(self.signal.directory+'/MakeFeatureArray/Output/feature_array.txt',
                        # usecols = self.features)
        self.train_sets['Signal'], self.test_sets['Signal'] = train_test_split(df)

    def get_bg_train_test_data(self, bg_name):
        df = pd.read_csv('MakeFeatureArrays/Output/'+bg_name+'/feature_array.txt',
                         usecols = self.features)
        # df = pd.read_csv('BackgroundFeatureArrays/Output/{}/feature_array.txt'.format(bg_name),
                         # usecols = self.features)
        self.train_sets[bg_name], self.test_sets[bg_name] = train_test_split(df,train_size = 0.3)
