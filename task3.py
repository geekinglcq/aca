 #coding:utf-8
from __future__ import print_function
from pylab import *
import Paper
import csv
from ILearner import SGDRegr
import numpy as np
import ast

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

zeroFeature=0
halfMissing=0

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

def SortAutAndReferred(res):
	keys=res.keys()
	keys.sort()
	ty=[len(res[k]) for k in keys]
	return keys,ty

def CompleteReferred(keys,ty):
	global halfMissing
	global zeroFeature
	if len(keys)>0:
		L=len(keys)
		if L<=(latest-keys[0]+1)/2:
			halfMissing=halfMissing+1
		time=keys[0]
		i=0
		while time<=latest:
			if i+1 < len(keys) and time+1 != keys[i+1]:
				keys.insert(i+1,time+1)
				ty.insert(i+1,ty[i])
			time=time+1
			i=i+1
		tmp=keys[-1]+1
		keys = keys+[i for i in range(tmp,latest+1)]
		ty = ty+[ty[-1] for i in range(tmp,latest+1)]
	else:
		zeroFeature=zeroFeature+1
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



def TrainAndValidation():
	readerCount=0
	train={}
	with open(name=unicode(trainPath,'utf8'),mode="r") as trainf:
		reader=csv.reader(trainf)
		first=True
		for row in reader:
			if first:
				first=False
				continue
			readerCount=readerCount+1
			train[row[0]]=int(row[1])

	D=int(np.ceil((latest-earliest+1)/timespan*1.0) )+1
	X=np.zeros((1,D),dtype=int)
	y=np.zeros((1,1),dtype=int)
	I=0
	for aut in train.keys():
		res,total = GroupReferedPaperByYear(aut)
		keys,ty=SortAutAndReferred(res)
		row=np.zeros((1,D),dtype=int)
		keys,ty = CompleteReferred(keys,ty)
		if len(keys)>0:
			for i in range(len(keys)):
				row[0, (keys[i]-earliest)/timespan ]=row[0,(keys[i]-earliest)/timespan ]+ty[i]
			X[I,:]=row
			X=np.concatenate((X,np.zeros((1,D),dtype=int)))
			y[I,:]=train[aut]
			y=np.concatenate((y,np.zeros((1,1),dtype=int)))
			I=I+1

	M = SGDRegr()
	print("trainning...")
	M.train(X,y)
	print("predicting...")
	with open(name=unicode(validationPath,'utf8'),mode="r") as csvf:
		with open(name=unicode(output3Path,'utf8'),mode="w") as out:
			reader=csv.reader(csvf)
			firstRow=True
			for row in reader:
				if firstRow:
					firstRow=False
					out.write("<task3>\nauthorname\tcitation\n")
					continue
				row=np.zeros((1,int(np.ceil((latest-earliest+1)/timespan*1.0))+1),dtype=int)
				res,total = GroupReferedPaperByYear(row[0])
				keys,ty = SortAutAndReferred(res)
				#todo 一起预测
				if len(keys)>0:
					keys,ty = CompleteReferred(keys,ty)
					for i in range(len(keys)):
						row[ 0,(keys[i]-earliest)/timespan ]=row[0, (keys[i]-earliest)/timespan ]+ty[i]
				A=M.predict(row)
				out.write("%s\t%d\n"%(row[0], A))
			out.write("</task3>\n")

def main():
	ParsePaperTxt()
	TrainAndValidation()



if __name__ == "__main__":
	main()

