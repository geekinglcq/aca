 #coding:utf-8
from __future__ import print_function
from pylab import *
import Paper
import csv
from ILearner import Svr
import numpy as np
import ast
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import random

# 文件路径
paperPath = "F:\\比赛数据\\task3\\papers.txt"
trainPath = "F:\\比赛数据\\task3\\train.csv"
validationPath="F:\\比赛数据\\task3\\validation.csv"
output3Path="F:\\比赛数据\\task3\\output3.txt"

tempPath="F:\\比赛数据\\task3\\temp3.txt"

# 特征参数
timespan = 5	#每5年的被引数为一个特征
earliest = 1936
latest = 2016

E=[]
zeroFeature=[]
zeroFAndZeroOut=0

def GroupReferedPaperByYear(author):
	res={}
	total=0
	papers = Paper.Paper.getPaperByAut(author)
	for paper in papers:
		for refed in paper.Referenced:
			total=total+1
			if refed.Time in res:
				res[refed.Time].append(refed)
			else:
				res[refed.Time] = [refed]
	return res,total

def SortAutAndReferred(res):
	keys=res.keys()
	keys.sort()
	ty=[len(res[k]) for k in keys]
	return keys,ty

def ParsePaperTxt():
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
def Train():
	global zeroFeature
	global zeroFAndZeroOut
	global E
	with open(name=unicode(trainPath,'utf8'),mode="r") as csvf:
		reader=csv.reader(csvf)
		firstRow=True
		for row in reader:
			if firstRow:
				firstRow=False
				continue
			res,total = GroupReferedPaperByYear(row[0])
			keys=res.keys()
			keys.sort()
			X=keys
			ty=[len(res[k]) for k in X]
			y=[sum(ty[0:i+1]) for i in range(len(X))]
			trainResult=int(row[1])
			if len(y)>0:
				svr = Svr(kernel='linear')
				svr.train(np.array(X).reshape(len(X),1), np.array(y).reshape(len(y),))
				Xp = [[2017]]
				yp = svr.predict(Xp)
				E.append(trainResult/yp[0])
			else:
				if trainResult>0:
					zeroFeature.append(trainResult)
				else:
					zeroFAndZeroOut=zeroFAndZeroOut+1

	#Save:
	with open(name=unicode(tempPath,'utf8'),mode="w") as fin:
		fin.write("%r\n"%zeroFeature)
		fin.write("%r\n"%zeroFAndZeroOut)
		fin.write("%r\n"%E)


def analysis():
	global zeroFeature
	global zeroFAndZeroOut
	global E

	with open(name=unicode(tempPath,'utf8'),mode="r") as fout:
		I=0
		for line in fout:
			if I==0:
				tzeroFeature=ast.literal_eval(line)
			elif I==1:
				zeroFAndZeroOut=ast.literal_eval(line)
			else:
				te=ast.literal_eval(line)
			I=I+1
	#系数分布
	#E=[i for i in te if i<=100]
	#ma=max(E)
	#mi=min(E)
	#nBins=int(ma-mi)
	#plt.figure()
	#n,bins,patches = plt.hist(E,nBins)
	#s=len(E)
	#expect=0.0
	#for i in range(100):
	#	expect=expect+i*(n[i]/s)
	#print("%r\t%r\t%r"%(ma,mi,expect))
	#plt.title("E")
	#plt.show()

	#零输入而最终有结果的分布
	zeroFeature = [i for i in tzeroFeature if i<=100]
	plt.figure()
	ma=max(zeroFeature)
	mi=min(zeroFeature)
	nBins=int(ma-mi)
	n,bins,patches = plt.hist(zeroFeature,nBins)
	expect=0.0
	s=len(zeroFeature)
	for i in range(99):
		expect=expect+i*(n[i]/s)
	print("%r\t%r\t%r"%(ma,mi,expect))
	plt.title("zero Result")
	plt.show()

	print("%r\t%r"%(zeroFAndZeroOut,zeroFAndZeroOut+len(zeroFeature)))


def Validation():
	with open(name=unicode(validationPath,'utf8'),mode="r") as csvf:
		with open(name=unicode(output3Path,'utf8'),mode="w") as out:
			reader=csv.reader(csvf)
			firstRow=True
			for row in reader:
				if firstRow:
					firstRow=False
					out.write("<task3>\nauthorname\tcitation\n")
					continue
				res,total = GroupReferedPaperByYear(row[0])
				keys=res.keys()
				keys.sort()
				X=keys
				ty=[len(res[k]) for k in X]
				y=[sum(ty[0:i+1]) for i in range(len(X))]
				A=0
				if len(y)>0:
					svr = Svr(kernel='linear')
					svr.train(np.array(X).reshape(len(X),1), np.array(y).reshape(len(y),))
					Xp = [[2017]]
					yp = svr.predict(Xp)
					A=int(yp[0]*12.4)
				out.write("%s\t%d\n"%(row[0], A))
			out.write("</task3>\n")


def main():
	ParsePaperTxt()
	#Train()

	Validation()
	#analysis()



if __name__ == "__main__":
	main()

