#coding: utf-8
#from __future__ import unicode_literals
import task3
import Paper
import codecs
import matplotlib.pyplot as plt
from ILearner import LIFT
from sklearn.model_selection import train_test_split
import datetime

# 文件路径
paperPath = "F:\\ACAData\\task3\\papers.txt"
trainPath = "F:\\ACAData\\task2\\training.txt"
labelsPath = "F:\\ACAData\\task2\\labels.txt"
validationPath = "F:\\ACAData\\task2\\validation.txt"
output2Path = "F:\\ACAData\\task2\\output2.txt"

trainX = []
trainY = []
testX = []
testX_r=[]
labels = []
labels_inv = {}
jor2no = {}

def ReadLabels():
    print("%s Read Labels" % datetime.datetime.now())
    with codecs.open(labelsPath, "r",encoding = 'utf-8') as fin:
        i = 0
        for row in fin:
            labels.append(row.strip())
            labels_inv[row.strip()] = i
            i = i + 1

def ReadTrain():
    print("%s Read Train" % datetime.datetime.now())
    with codecs.open(trainPath, "r",'utf-8') as fin:
        i = 0
        for row in fin:
            if i % 3 == 0:
                trainX.append(row.strip())
            elif i % 3 == 1:
                trainY.append([s.strip() for s in row.split(',')])
            else:
                pass
            i = i + 1

def ReadValidation():
    print("%s Read Validation" % datetime.datetime.now())
    with codecs.open(validationPath, "r",encoding ='utf-8') as fin:
        i = 0
        for row in fin:
            if i % 2 == 0:
                testX.append(row.strip())
            else:
                pass
            i = i + 1

def GroupPaperByJor(aut):
    papers = Paper.Paper.getPaperByAut(aut)
    d = {}
    for paper in papers:
        if not paper.Journal in d:
            d[paper.Journal] = 0
        d[paper.Journal] = d[paper.Journal] + 1
    return d

def reformatData(X,Y):
    """
    X - Vector of Name
    Y - Vector of Vec3sz of interests
    """
    _x = []
    _y = []
    for x in X:
        #{ jor:num }
        m = GroupPaperByJor(x)
        t = [0 for i in range(len(jor2no))]
        for item in m.items():
            t[jor2no[item[0]]] = item[1]
        _x.append(t)

    for y in Y:
        t = [0 for i in range(len(y))]
        for i in range(len(y)):
            t[i] = labels_inv[y[i]]
        _y.append(t)
    return _x,_y


def SelectModel():
    print("%s select Model" % datetime.datetime.now())
    X_train, X_test, y_train, y_test = train_test_split(trainX, trainY, test_size=0.3, random_state=0)

    #Train:
    model = LIFT(1,range(len(labels)))
    model.train(X_train,y_train)
    print("score: %r\n" % (model.score(X_test,y_test)))

    return model

def GenResult(model):
    print("%s Prediction..." % datetime.datetime.now())
    y = model.predict(testX_r)
    #Validation:
    with codecs.open(output2Path,'w',encoding = 'utf-8') as fout:
        fout.write(u"<task2>\nauthorname\tinterest1\tinterest2\tinterest3\tinterest4\tinterest5\n")
        for V in y:
            while len(V) < 5:
                V.append(0)
            fout.write(u"%s\t%s\t%s\t%s\t%s\t%s\t\n" % (testX[i],labels[V[0]],labels[V[1]],labels[V[2]],labels[V[3]],labels[V[4]]))
        fout.write(u"</task2>\n")


def analisis():
	#统计各期刊上，兴趣的分布
	r = {}
	for i in range(len(trainX)):
		papers = Paper.Paper.getPaperByAut(trainX[i])
		jur = set([p.Journal for p in papers])
		for j in jur:
			if not j in r:
				r[j] = {}
			for it in trainY[i]:
				if not it in r[j]:
					r[j][it] = 0
				r[j][it] = r[j][it] + 1
	#raw_input('wait attach')
	for k,v in r.items():
		plt.figure()
		mh = max(v.values())
		ind = []
		h = []
		lab = []
		val = v.values()
		for i in range(len(v)):
			if val[i] > mh * 0.5:
				h.append(val[i])
				ind.append(i)
				lab.append(v.keys()[i])
		b = plt.bar(ind,h,tick_label=lab)
		plt.title(k)
		plt.show()

def Preprocess():
    print("%s preprocess" % datetime.datetime.now())
    sjor = set([item[1].Journal for item in Paper.Paper._Paper__wholeData.items()])
    id = 0
    for j in sjor:
        jor2no[j] = id
        id = id + 1
    del(sjor)

    global trainX,trainY,testX,testX_r
    trainX, trainY = reformatData(trainX,trainY)
    testX_r, dummy = reformatData(testX,[])

    Paper.Paper.RemoveAllData()

def main():
    task3.ParsePaperTxt()
    ReadLabels()
    ReadTrain()
    ReadValidation()
    Preprocess()
    m = SelectModel()
    GenResult(m)

if __name__ == "__main__":
	main()