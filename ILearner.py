from sklearn.svm import SVR
from sklearn import linear_model
import numpy as np
import Paper
import datetime

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
        with open(fileName,'w') as fout:
            for k,v in self.weightPool.items():
                fout.write('%r,%r\n'%(k,v))
                
    def load(self,fileName):
        with open(fileName,'r') as fin:
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
        with (open(('%r_cv.txt' % self.C), mode='w')) as fout:
            for i in range(N):
                fout.write("%r,%r,%r\n" % (Xv[i], Yv[i], YP[i]))
        return 1 - 1.0 / N * s

class task2Learner(ILearner):
    def __init__(self):
        self.summary={}

    def train(self, X, y):
        r={}
        for i in range(len(X)):
            papers = Paper.Paper.getPaperByAut(X[i])
            jur = set([p.Journal for p in papers])
            for j in jur:
                if not j in r:
                    r[j]={}
                for it in y[i]:
                    if not it in r[j]:
                        r[j][it]=0
                    r[j][it]=r[j][it]+1
        for k,v in r.items():
            mh = max(v.values())
            it = [(p,q) for (p,q) in v.items() if q>mh*0.5]
            self.summary[k]=it

    def predict(self, X):
        y=[]
        for i in range(len(X)):
            aut=X[i]
            papers = Paper.Paper.getPaperByAut(aut)
            jur = set([p.Journal for p in papers])
            tmp=[]
            count={}
            for j in jur:
                #todo : if not in??
                if j in self.summary:
                    tus = self.summary[j]
                    for tu in tus:
                        if not tu[0] in count:
                            count[tu[0]]=0
                        count[tu[0]]=count[tu[0]]+tu[1]
            l=sorted(count.items(),key=lambda d:d[1],reverse=True)
            V = [v[0] for v in l]
            y.append(V[0:10])
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
