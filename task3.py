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
paperPath = "F:\\ACAData\\task3\\papers.txt"
trainPath = "F:\\ACAData\\task3\\train.csv"
validationPath="F:\\ACAData\\task3\\validation.csv"
output3Path="F:\\ACAData\\task3\\output3.txt"

tempPath="F:\\ACAData\\task3\\temp3.txt"

cited={}
map=Svr('linear')

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

def GroupReferedPaper(id):
	res={}
	paper=Paper.Paper.getPaperById(id)
	for refed in paper.Referenced:
		if refed.Time in res:
			res[refed.Time].append(refed)
		else:
			res[refed.Time]=[refed]
	return res

def SortAutAndReferred(res):
	keys=res.keys()
	keys.sort()
	ty=[len(res[k]) for k in keys]
	return keys,ty

def ParsePaperTxt():
	with open(name=paperPath,mode="rU") as f:
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
	Id = 0
	j=0
	color=['b','g','r','c','m']
	while Id in Paper.Paper._Paper__wholeData:
		res = GroupReferedPaper(Id)
		X = res.keys()
		if len(X)>0:
			X.sort()
			ty = [len(res[k]) for k in X]
			y=[sum(ty[0:i+1]) for i in range(len(X))]
			#plt.plot(X,y,color[j%5],label=str(Id))

			if len(X)>2:
				xp=X[-3:]
				yp=y[-3:]
			else:
				xp=X
				yp=y
			svr = Svr('linear')
			svr.train(  np.array(xp).reshape(len(xp),1),  np.array( yp ).reshape(len(yp),)  )
			xp.append(2017)
			yp = svr.predict(np.array(xp).reshape(len(xp),1))
			cited[Id]=int(yp[-1])
			#plt.plot(xp,yp,color[j%5]+'--')
			#j=j+1
			#if j%5==0:
			#	plt.legend()
			#	plt.show()
		else:
			cited[Id]=0
		Id=Id+1
		
	with open(name=trainPath,mode="r") as csvf:
		with open(name=tempPath,mode="w") as outf:
			reader=csv.reader(csvf)
			firstRow=True
			for row in reader:
				if firstRow:
					firstRow=False
					continue
				papers = Paper.Paper.getPaperByAut(row[0])
				s=0
				for paper in papers:
					s=s+cited[paper.Index]
				outf.write("%r,%r\n"%(s,int(row[1])))

def analysis():
	global map
	d={}
	with open(name=tempPath,mode="r") as fin:
		for line in fin:
			l=line.split(',')
			#if int(l[0]) in d:
			#	print("warning: %r already in d, old value is: %r was substituded by: %r\n"%(int(l[0]),d[int(l[0])],int(l[1])))
			d[int(l[0])]=int(l[1])
	X=d.keys()
	X.sort()
	y=[d[k] for k in X]
	map=Svr('linear')
	map.train(np.array(X).reshape(len(X),1),  np.array( y ).reshape(len(y),))
	Xp = range(X[0],X[-1]+1)
	yp = map.predict(np.array(Xp).reshape(-1,1))
	plt.plot(X,y,Xp,yp)
	plt.show()

def Validation():
	with open(name=validationPath,mode="r") as csvf:
		with open(name=output3Path,mode="w") as out:
			reader=csv.reader(csvf)
			firstRow=True
			for row in reader:
				if firstRow:
					firstRow=False
					out.write("<task3>\nauthorname\tcitation\n")
					continue
				papers = Paper.Paper.getPaperByAut(row[0])
				s=0
				for paper in papers:
					s=s+cited[paper.Index]
				#yp=map.predict([[s]])
				#A=yp[0]
				#if A<0:
				#	A=s
				out.write("%s\t%d\n"%(row[0], s*10))
			out.write("</task3>\n")

def main():
	ParsePaperTxt()
	Train()
	#analysis()
	Validation()



if __name__ == "__main__":
	main()

