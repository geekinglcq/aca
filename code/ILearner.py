from sklearn.svm import SVR
from sklearn import linear_model
import numpy as np
import Paper
import random

class ILearner(object):
    """description of class"""

    def train(self, X, y):
        pass

    def predict(self, X):
        pass


class Svr(ILearner):

    def __init__(self, kernel='rbf', degree=3, gamma='auto', coef0=0.0,
                 tol=0.001, C=1.0, epsilon=0.1, shrinking=True, cache_size=200,
                 verbose=False, max_iter=-1):
        self.kernel = kernel
        self.C = C
        self.gamma = gamma
        self.coef0 = coef0
        self.tol = tol
        self.epsilon = epsilon
        self.shrinking = shrinking
        self.cache_size = cache_size
        self.verbose = verbose
        self.max_iter = max_iter
        self.model = SVR(kernel=self.kernel, C=self.C, gamma=self.gamma,
                         coef0=self.coef0, tol=self.tol, epsilon=self.epsilon,
                         shrinking=self.shrinking, cache_size=self.cache_size,
                         verbose=self.verbose, max_iter=self.max_iter)

    def train(self, X, y):
        self.model.fit(X, y)
        pass

    def predict(self, X):
        return self.model.predict(X)


class SGDRegr(ILearner):

    def __init__(self):
        self.clf = linear_model.SGDRegressor(n_iter=50)

    def train(self, X, y):
        self.clf.fit(X, y)

    def predict(self, X):
        return self.clf.predict(X)


class SparsePA(ILearner):

    def __init__(self, C, T):
        self.weightPool = {}
        self.C = C
        self.T = T


    def __makeOnePrediction(self,aut):
        w=[]
        x=[]
        papers = Paper.Paper.getPaperByAut(aut)
        for paper in papers:
            t=len(paper.Referenced)
            p=0.0
            if paper.Index in self.weightPool:
                p=self.weightPool[paper.Index]
            if t==0:
                t=1
            w.append(p)
            x.append(t)
        w=np.array(w).reshape((1,-1))
        x=np.array(x).reshape((-1,1))
        
        yp = w.dot(x)[0, 0]
        return yp,w,x

    def train(self, X, Y):
        """X - List of ['Name']\nY - List of [Citaion]"""

        for k in range(self.T):
            print("Training: %d\n" % (k))
            for i in range(len(X)):
                y=Y[i]
                yp,w,x = self.__makeOnePrediction(X[i])

                loss = abs(yp - y)
                tau = loss /  np.sum(x**2)
                w = w + np.sign(y - yp) * tau * x.T

                j=0
                papers = Paper.Paper.getPaperByAut(X[i])
                for paper in papers:
                    self.weightPool[paper.Index]=w[0,j]
                    j=j+1

    def predict(self, X):
        """X - List of ['Name'] """
        Y = [0 for x in X]
        for i in range(len(X)):
            yp,w,x = self.__makeOnePrediction(X[i])
            if(yp<0):
                yp=0
            Y[i] = int(round(yp))
        return Y

    def MAPEScore(self, Xv, Yv):
        YP = self.predict(Xv)
        s = 0
        N = len(Yv)
        for i in range(N):
            if YP[i] != 0 or Yv[i] != 0:
                s = s + abs(YP[i] - Yv[i]) * 1.0 / max(YP[i], Yv[i])
        #with (open(('%r_cv.txt'%self.C),mode='w')) as fout:
        #    for i in range(N):
        #        fout.write("%r,%r,%r\n"%(Xv[i],Yv[i],YP[i]))
        return 1 - 1.0 / N * s
    def save(self,fileName):
        with open(fileName,'w') as fout:
            for k,v in self.weightPool.items():
                fout.write('%r,%r\n'%(k,v))
                
    def load(self,fileName):
        with open(fileName,'r') as fin:
            for row in fin:
                it=row.split(',')
                self.weightPool[int(it[0])] = float(it[1])
