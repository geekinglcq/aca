 #coding:utf-8
from pylab import *
import Paper
import csv
from ILearner import Svr
import numpy as np

# 文件路径
paperPath = "F:\\比赛数据\\task3\\papers.txt"
trainPath = "F:\\比赛数据\\task3\\train.csv"
validationPath="F:\\比赛数据\\task3\\validation.csv"
output3Path="F:\\比赛数据\\task3\\output3.txt"


def GroupReferedPaperByYear(author):
	res={}
	total=0
	papers = Paper.Paper.getPaperByAut(author)
	for paper in papers:
		for refed in paper.Referenced:
			total=total+1
			if res.has_key(refed.Time):
				res[refed.Time].append(refed)
			else:
				res[refed.Time] = [refed]
	return res,total

with open(name=unicode(paperPath,'utf8'),mode="rU") as f:
	for eachLine in f:
		if eachLine.startswith('#index'):
			i = int(eachLine[6:])
			p=Paper.Paper.getPaperById(i)
		elif eachLine.startswith("#@"):
			p.Author = eachLine[2:-1].split(',')
			for aut in p.Author:
				Paper.Paper.addAutPaper(aut,p)
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


while True:
	aut = raw_input("author Name:")
	if aut=="-1":
		break
	res,total = GroupReferedPaperByYear(aut)
	for k,v in res.items():
		print "%d %d"%(k,len(v))
	print total


# todo : 计算误差，选择模型，保存模型
with open(name=unicode(validationPath,'utf8'),mode="r") as csvf:
	with open(name=unicode(output3Path,'utf8'),mode="w") as out:
		reader=csv.reader(csvf)
		firstRow=True
		for row in reader:
			if firstRow:
				firstRow=False
				out.write("<task3>\nauthorname	citation\n")
				continue
			res,total = GroupReferedPaperByYear(row[0])
			keys=res.keys()
			keys.sort()
			X=keys
			ty=[len(res[k]) for k in X]
			y=[sum(ty[0:i+1]) for i in range(len(X))]
			if len(y)>0:
				svr = Svr(kernel='linear')
				svr.train(np.array(X).reshape(len(X),1), np.array(y).reshape(len(y),))
				Xp = [[2017]]
				yp = svr.predict(Xp)
				out.write("%s\t%d\n"%(row[0], int(yp[0]) ))
			else:
				out.write("%s\t%d\n"%(row[0], 0 ))
		out.write("</task3>\n")



"""
rng=np.random.RandomState(0)
X=rng.rand(1000,1)*2*3.14159
Xp = rng.rand(100,1)*6*3.14159-2*3.14159
y=np.sin(X).ravel()
svr = Svr('rbf',10,0.1)
svr.train(X,y)
yp=svr.predict(Xp)
plt.figure()
plt.scatter(X,y,c='r',label='SVR',zorder=2)
plt.scatter(Xp,yp,c='b',label='Predict',zorder=1)
plt.xlabel('data')
plt.ylabel('target')
plt.title('SVR versus Kernel Ridge')
plt.legend()
plt.show()
"""