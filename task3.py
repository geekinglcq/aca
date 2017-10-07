# coding:utf-8
import Paper
import csv
from ILearner import SparsePA
from sklearn.model_selection import train_test_split
import pickle


# 文件路径
paperPath = "F:\\ACAData\\task3\\papers.txt"
trainPath = "F:\\ACAData\\task3\\train.csv"
validationPath = "F:\\ACAData\\task3\\validation.csv"
testPath= "F:\\ACAData\\task3\\test.csv"
output3Path = "F:\\ACAData\\task3\\output3.txt"

tempPath = "F:\\ACAData\\task3\\temp3.txt"


trainX = []
trainY = []
testX = []
epsilon = 0.7
finalTestX=[]


def GroupReferedPaperByYear(author):
    res = {}
    total = 0
    papers = Paper.Paper.getPaperByAut(author)
    for paper in papers:
        for refed in paper.Referenced:
            total = total + 1
            if refed.Time in res:
                res[refed.Time].append(refed)
            else:
                res[refed.Time] = [refed]
    return res, total


def ParsePaperTxt():
    with open(paperPath, "r") as f:
        for eachLine in f:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                p = Paper.Paper.getPaperById(i)
            elif eachLine.startswith("#@"):
                p.Author = eachLine[2:-1].split(',')
                for aut in p.Author:
                    Paper.Paper.addAutPaper(aut, p)
            elif eachLine.startswith("#*"):
                p.Title = eachLine[2:-1]
            elif eachLine.startswith("#t"):
                p.Time = int(eachLine[2:-1])
            elif eachLine.startswith("#c"):
                p.Journal = eachLine[2:-1]
            elif eachLine.startswith("#%"):
                t = Paper.Paper.getPaperById(int(eachLine[2:-1]))
                p.References.append(t)
                t.Referenced.append(p)
            else:
                pass


def ReadTrain():
    with open(name=trainPath, mode="r") as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            trainX.append(row[0])
            trainY.append(int(row[1]))


def ReadValidation():
    with open(name=validationPath, mode="r") as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            testX.append(row[0])

def ReadTest():
    with open(testPath,"r") as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow=False
                continue
            finalTestX.append(row[0])

def SelectModel():
    X_train, X_test, y_train, y_test = train_test_split(
        trainX, trainY, test_size=0.3, random_state=0)
    #c=0
    #opt = 0
    ##standard : 0.9830
    #while True:
    #    m = SparsePA(c, 20)
    #    xtmp,ytmp = m.train(trainX, trainY)
    #    mape = m.MAPEScore(X_test, y_test)
    #    print("C: %r,  MAPE: %r, train: %r,test: %r\n" % (c, mape,len(X_train),len(X_test)))
    #    if mape > opt:
    #        opt = mape
    #        model = m
    #        model.save('mape%.5f.txt'%mape)
    #        pickle.dump(xtmp,open("xmp.pkl",'wb'))
    #        pickle.dump(ytmp,open("ymp.pkl",'wb'))

    X=pickle.load(open("xmp.pkl","rb"))
    Y=pickle.load(open('ymp.pkl','rb'))
    m = SparsePA(0,1020)
    m.load('mape0.98366.txt')
    m.train(X,Y)
    mape = m.MAPEScore(X_test,y_test)
    m.save('optmodel.txt')
    print("MAPE: %r\n" % (mape))
    return m



def GenResult(model):
    with open(name=output3Path, mode="w") as out:
        out.write("<task3>\nauthorname\tcitation\n")
        Yp = model.predict(testX)
        for i in range(len(Yp)):
            out.write("%s\t%d\n" % (testX[i], Yp[i]))
        out.write("</task3>\n")

def GenTestResult(model):
    with open(name=output3Path, mode="w") as out:
        out.write("<task3>\nauthorname\tcitation\n")
        Yp = model.predict(finalTestX)
        for i in range(len(Yp)):
            out.write("%s\t%d\n" % (finalTestX[i], Yp[i]))
        out.write("</task3>\n")

def main():
    ParsePaperTxt()
    ReadTrain()
    ReadValidation()
    #ReadTest()
    model = SelectModel()
    GenResult(model)
    #GenTestResult(model)


if __name__ == "__main__":
    main()
