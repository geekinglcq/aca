# coding:utf-8
import Paper
import csv
import ILearner
from sklearn.model_selection import train_test_split
import datetime
import pickle


# 文件路径
paperPath = "./task3/papers.txt"
trainPath = "F:\\ACAData\\task3\\train.csv"
validationPath = "F:\\ACAData\\task3\\validation.csv"
output3Path = "F:\\ACAData\\task3\\output3.txt"

trainX = []
trainY = []
testX = []

def ParsePaperTxt():
    print("%s parse paper"%datetime.datetime.now())
    with open(paperPath, "r",encoding='utf-8') as f:
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
    print("%s read training set"%datetime.datetime.now())
    with open(trainPath, "r",encoding='utf-8') as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            trainX.append(row[0])
            trainY.append(int(row[1]))


def ReadValidation():
    print("%s read validation set"%datetime.datetime.now())
    with open(validationPath, "r",encoding='utf-8') as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            testX.append(row[0])


def SelectModel():
    print("%s select model"%datetime.datetime.now())
    X_train, X_test, y_train, y_test = train_test_split(
        trainX, trainY, test_size=0.3, random_state=0)
<<<<<<< HEAD
    C = [0]
    opt = 0
    for c in C:
        m = SparsePA(c, 5)
        m.train(trainX, trainY)
        mape = m.score(X_test, y_test)
        print("C: %r,  MAPE: %r, train: %r, test: %r\n" %
              (c, mape, len(trainY), len(y_test)))
        if mape > opt:
            opt = mape
            model = m
=======
    c=0
    #m = SparsePA(c, 1000)
    m = ILearner.DNN()
    m.train(trainX, trainY)
    mape = m.score(X_test, y_test)
    print("C: %r,  MAPE: %r, train: %r, test: %r\n" %
          (c, mape, len(trainY), len(y_test)))
    if mape > opt:
        opt = mape
        model = m
>>>>>>> f2d12d0... cannot run
    return model


def GenResult(model):
    print("%s save model"%datetime.datetime.now())
    with open(output3Path, "w",encoding='utf-8') as out:
        out.write("<task3>\nauthorname\tcitation\n")
        Yp = model.predict(testX)
        for i in range(len(Yp)):
            out.write("%s\t%d\n" % (testX[i], Yp[i]))
        out.write("</task3>\n")


def analisis():
    tempPath = "F:\\ACAData\\task3\\"
    with open(tempPath+"temp.txt",'w',encoding='utf-8') as fout:
        fout.write("%r\n"%len(trainX))
        for i in range(len(trainX)):
            papers = Paper.Paper.getPaperByAut(trainX[i])
            A = [(papers[j].Index, len(papers[j].Referenced)) for j in range(len(papers))]
            for j in range(len(A)):
                fout.write("%d:%d;"%(A[j][0],A[j][1]))
            fout.write("%d\n"%trainY[i])


def main():
    ParsePaperTxt()
    #Paper.Paper.MergerPaper()
    ReadTrain()
    analisis()
    ReadValidation()
    model = SelectModel()
    model.save('optModel.txt')
    GenResult(model)




if __name__ == "__main__":
    main()

