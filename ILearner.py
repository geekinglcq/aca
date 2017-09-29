from sklearn.svm import SVR
from sklearn import svm
from sklearn import linear_model
from sklearn.cluster import KMeans
import numpy as np
import Paper
import datetime
import math
import random
import codecs

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

    def __makeOnePrediction(self, aut, **args):
        w = []
        x = []
        papersIds = Paper.Paper._Paper__authorToIndexes[aut]
        gids=set( [ Paper.Paper._Paper__IndexToGroup[ pid ] for pid in papersIds]  )
        for gid in gids:
            t = Paper.Paper._Paper__GroupData[gid]
            p = 1.0
            if gid in self.weightPool:
                p = self.weightPool[gid]
            if t == 0:
                t = 1
            w.append(p)
            x.append(t)
        w = np.array(w).reshape((1, -1))
        x = np.array(x).reshape((-1, 1))

        yp = w.dot(x)[0, 0]
        if 'y' in args:
            y = args['y']
            loss = abs(yp - y)
            if self.C==0:
                tau = loss / np.sum(x**2)
            else:
                tau = loss / (1.0 / (2 * self.C) + np.sum(x**2))
            w = w + np.sign(y - yp) * tau * x.T
            tmp = int(round(yp))
            if (tmp != 0 and y == 0) or (tmp == 0 and y != 0):
                self.__needRefine.add((aut, args['y']))
        return int(round(yp)), w, gids

    def save(self,fileName):
        with codecs.open(fileName,'w',encoding='utf-8') as fout:
            for k,v in self.weightPool.items():
                fout.write('%r,%r\n'%(k,v))
                
    def load(self,fileName):
        with codecs.open(fileName,'r',encoding='utf-8') as fin:
            for row in fin:
                it=row.split(',')
                self.weightPool[int(it[0])] = float(it[1])

    def train(self, X, Y):
        """X - List of ['Name']\nY - List of [Citaion]"""
        for k in range(self.T):
            self.__needRefine = set()
            print("%s  Training: %d" % (datetime.datetime.now(), k))
            for i in range(len(X)):
                yp, w, ids = self.__makeOnePrediction(X[i], y=Y[i])
                j=0
                for id in ids:
                    self.weightPool[id] = w[0, j]
                    j=j+1
            for sam in self.__needRefine:
                yp, w, ids = self.__makeOnePrediction(sam[0], y=sam[1])
                j=0
                for id in ids:
                    self.weightPool[id] = w[0, j]
                    j=j+1

    def predict(self, X):
        """X - List of ['Name'] """
        Y = [0 for x in X]
        for i in range(len(X)):
            yp, w, ids = self.__makeOnePrediction(X[i])
            if yp < 0:
                yp = -yp
            Y[i] = yp
        return Y

    def score(self, Xv, Yv):
        YP = self.predict(Xv)
        s = 0
        N = len(Yv)
        for i in range(N):
            if YP[i] != 0 or Yv[i] != 0:
                s = s + abs(YP[i] - Yv[i]) * 1.0 / max(YP[i], Yv[i])
        with ( codecs.open(('%r_cv.txt' % self.C), 'w',encoding='utf-8' ) ) as fout:
            for i in range(N):
                #fout.write("%r,%r,%r\n" % (Xv[i], Yv[i], YP[i]))
                fout.write("%r\t%r\n"%(Xv[i],Yv[i]))
        return 1 - 1.0 / N * s

class LIFT(ILearner):
    def __init__(self, r, LabelSpace):
        self.models=[]
        self.r = r
        self.LabelSpace = LabelSpace
        self.ansLen=5

    def _distance(self,x,y):
         return np.sqrt( np.sum( np.power( np.array(x)-np.array(y),2) ) )

    def train(self, X, y):
        y=np.array(y)
        q = len(self.LabelSpace)
        M = np.size(X,0)
        for k in range(q):
            Pk = [X[i] for i in range(M) if self.LabelSpace[k] in y[i]]
            Nk = [X[i] for i in range(M) if not self.LabelSpace[k] in y[i]]
            mk = self.r * min(len(Pk),len(Nk))
            #todo: choose another cluster method
            centp = KMeans(mk).fit(Pk).cluster_centers_
            centn = KMeans(mk).fit(Nk).cluster_centers_
            PhiK=[]
            Yk=[0 for i in range(M)]
            for i in range(M):
                tp = [ self._distance(Pk[i],centp[j]) for j in range(mk) ]
                tn = [ self._distance(Pk[i],centn[j]) for j in range(mk) ]
                tp.extend(tn)
                PhiK.append(tp)
                if self.LabelSpace[k] in y[i]:
                    Yk[i]=1
                else:
                    Yk[i]=0

            #todo: choose another classification method and adjust parameters
            clf = svm.SVC()
            clf.fit(PhiK,Yk)
            self.models.append(clf)


    def predict(self, X):
        y=[]
        for i in range(len(X)):
            t=[-1 for i in range(self.ansLen+1)]
            p=[-1 for i in range(self.ansLen+1)]
            for k in len(self.LabelSpace):
                R = self.models[k]._predict_proba(X[i])
                j = self.ansLen
                while j>0 and p[j-1]<R[1]:
                   p[j]=p[j-1]
                   t[j]=t[j-1]
                   j=j-1
                p[j] = R[1]
                t[j]=k
            y.append(t)
        return y

    def score(self,Xv,Yv):
        YP=self.predict(Xv)
        N=len(Xv)
        s=0
        for i in range(N):
            s1=set(YP[i])
            s2=set(Yv[i])
            s=s+len(s1.intersection(s2))/3.0
        return s/N

