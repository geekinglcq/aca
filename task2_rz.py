#coding: utf-8
import task3
import Paper
import codecs
import matplotlib.pyplot as plt
from ILearner import task2Learner
from sklearn.model_selection import train_test_split

# 文件路径
trainPath = "F:\\ACAData\\task2\\training.txt"
validationPath = "F:\\ACAData\\task2\\validation.txt"
output2Path = "F:\\ACAData\\task2\\output2.txt"

trainX = []
trainY = []
testX = []

def ReadTrain():
    with codecs.open(trainPath, "r",'utf-8') as fin:
        i=0
        for row in fin:
            if i%3==0:
                trainX.append(row.strip())
            elif i%3==1:
                trainY.append([s.strip() for s in row.split(',')])
            else:
                pass
            i=i+1

def ReadValidation():
    with codecs.open(validationPath, "r",'utf-8') as fin:
        i=0
        for row in fin:
            if i%2==0:
                testX.append(row.strip())
            else:
                pass
            i=i+1

def TrainAndOutput():
    #Train:
    model = task2Learner()
    X_train, X_test, y_train, y_test = train_test_split(
        trainX, trainY, test_size=0.3, random_state=0)

    model.train(X_train,y_train)
    print("score: %r\n"%(model.score(X_test,y_test)))

    #Validation:
    #with codecs.open(output2Path,'w','utf-8') as fout:
    #    fout.write(u"<task2>\nauthorname\tinterest1\tinterest2\tinterest3\tinterest4\tinterest5\n")
    #    for V in y:
    #        while len(V)<5:
    #            V.append('dummy')
    #        fout.write(u"%s\t%s\t%s\t%s\t%s\t%s\t\n"%(aut,V[0],V[1],V[2],V[3],V[4]))
    #    fout.write(u"</task2>\n")
    #print("%r/%r\n"%(t,len(testX)))


def analisis():
    #统计各期刊上，兴趣的分布
    r={}
    for i in range(len(trainX)):
        papers = Paper.Paper.getPaperByAut(trainX[i])
        jur = set([p.Journal for p in papers])
        for j in jur:
            if not j in r:
                r[j]={}
            for it in trainY[i]:
                if not it in r[j]:
                    r[j][it]=0
                r[j][it]=r[j][it]+1
    #raw_input('wait attach')
    for k,v in r.items():
        plt.figure()
        mh = max(v.values())
        ind=[]
        h=[]
        lab=[]
        val=v.values()
        for i in range(len(v)):
            if val[i]>mh*0.5:
                h.append(val[i])
                ind.append(i)
                lab.append(v.keys()[i])
        b = plt.bar(ind,h,tick_label=lab)
        plt.title(k)
        plt.show()



def main():
    task3.ParsePaperTxt()
    ReadTrain()
    ReadValidation()
    TrainAndOutput()
    #analisis()


if __name__ == "__main__":
    main()