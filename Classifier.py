from __future__ import division
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier 
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.metrics import roc_curve, auc
from myProcesses import myProcesses
from SignalProcess import SignalProcess
from sklearn.externals import joblib
from helper_functions import get_SAF_objects
from helper_classes import Counter
from CutFlowTable import CutFlowTable
import untangle

class Classifier:

    processes = myProcesses()
    X_train = None
    X_train = None
    X_test = None
    y_train = None
    y_test = None

    def __init__(self, mass_combo):
        self.signal = SignalProcess(mass_combo)
        self.backgrounds = self.processes.backgrounds
        self.clf = GradientBoostingClassifier(verbose=2,
                                              loss = 'exponential')

        self.features = ['met', 'm_ll', 'm_bb', 'm_R', 'm_T_R']
        self.get_train_test_data(mass_combo)
        self.train()
        # self.save_as_pickle('pickled_classifier.pkl')

    def get_train_test_data(self, mass_combo):

        self.signal.get_train_test_data(self.features, train_size = 0.8)

        for background in self.backgrounds:
            background.get_train_test_data(self.features, train_size = 0.5)

        self.X_train=pd.concat([self.signal.training_set]+[bg.training_set for bg in self.backgrounds]) 
        self.X_test=pd.concat([self.signal.test_set]+[bg.test_set for bg in self.backgrounds]) 

        y_train_bgs = [np.zeros(bg.training_set.shape[0]) for bg in self.backgrounds]
        y_train_signal = [np.ones(self.signal.training_set.shape[0])]

        self.y_train = np.concatenate(tuple(y_train_signal+y_train_bgs))

        y_test_bgs = [np.zeros(bg.test_set.shape[0]) for bg in self.backgrounds]
        y_test_signal = [np.ones(self.signal.test_set.shape[0])]

        self.y_test = np.concatenate(tuple(y_test_signal+y_test_bgs))

    def train(self):
        self.clf.fit(self.X_train, self.y_train)

    def save_as_pickle(self, filename):
        joblib.dump(self.clf, filename)

    def make_roc_auc_curve(self):

        decisions = self.clf.decision_function(self.X_test)
        y_predicted = self.clf.predict(self.X_test)

        # Unleashing our classifier on the test data

        print(classification_report(self.y_test, y_predicted,
                                        target_names=["background", "signal"]))

        print("Area under ROC curve: %.4f"%(roc_auc_score(self.y_test,decisions)))
                                                            
        # Unleashing our classifier on the training data
        y_predicted = self.clf.predict(self.X_train)

        print classification_report(self.y_train, y_predicted,
                                        target_names=["background", "signal"])
        print "Area under ROC curve: %.4f"%(roc_auc_score(self.y_train,
                            self.clf.decision_function(self.X_train)))

        # Check for false positives
        # Compute ROC curve and area under the curve
        fpr, tpr, thresholds = roc_curve(self.y_test, decisions)
        roc_auc = auc(fpr, tpr)

        matplotlib.style.use('ggplot')
        plt.plot(fpr, tpr, lw=1, label='ROC (area = %0.5f)'%(roc_auc))

        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.grid()
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc="lower right")
        plt.savefig('roc_auc_curve.pdf')
        plt.close()

    # Compare training and test data 
    def compare_train_test(self):
        decisions = []
        for X,y in ((self.X_train, self.y_train), (self.X_test, self.y_test)):
            d1 = self.clf.decision_function(X[y>0.5]).ravel()
            d2 = self.clf.decision_function(X[y<0.5]).ravel()
            decisions += [d1, d2]

        low = min(np.min(d) for d in decisions)
        high = max(np.max(d) for d in decisions)
        low_high = (low,high)

        # Plotting the training data
        plt.hist(decisions[0],color='DarkBlue', alpha=0.4, range=low_high,
            bins=40, normed=True,label='Signal (training set)')

        plt.hist(decisions[1],color='Crimson', alpha=0.4, range=low_high,
            bins=40, normed=True,label='Combined Background (training set)')

        # Plotting the test events
        hist, bins = np.histogram(decisions[2],bins=40, range=low_high, 
                normed=True)
                                
        scale = len(decisions[2]) / sum(hist)

        err = np.sqrt(hist * scale) / scale

        width = (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        plt.errorbar(center, hist, yerr=err, fmt='o', c='DarkBlue', 
                label='Signal (test set)')

        hist, bins = np.histogram(decisions[3],bins=40, range=low_high, 
                                  normed=True)
            
        scale = len(decisions[2]) / sum(hist)
        err = np.sqrt(hist * scale) / scale

        plt.errorbar(center, hist, yerr=err, fmt='o', c='Crimson',
                label='Combined Background (test set)')

        plt.ylim(0, 0.35)
        plt.xlim(-10.,10.)
        plt.xlabel("BDT output (decision function)")
        plt.ylabel("Proportion of events (normalized to 1)")
        plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig('compare_train_test.pdf')
        plt.close()

    def bdt_response_histo(self):
        d1 = self.clf.decision_function(self.signal.test_set)
        d2, d3, d4 = [self.clf.decision_function(bg.test_set) for bg in self.backgrounds] 
        plt.hist(d1, label = 'Signal', bins = 40, normed = True, 
                alpha = 0.4, color = 'DarkBlue')
        plt.hist(d2, label = r'$tt$', bins = 40, normed = True, 
                alpha = 0.4, color = 'Crimson')
        (n, bins, patches) = plt.hist(d3, label = r'$tbW$', normed = True, 
                bins =40, alpha = 0.4, color = 'green')
        plt.hist(d4, label = r'$bbWW$', bins = 40, normed = True, 
                alpha = 0.4, color = 'orange')

        plt.ylim(0., 0.4)
        plt.xlim(-10., 10.)
        plt.legend(loc='best')
        plt.xlabel('BDT response')
        plt.ylabel('Fraction of events')
        plt.savefig('BDT_response.pdf')
        plt.close()

