#coding: utf-8
#from __future__ import unicode_literals
import task3
import Paper
import codecs
import matplotlib.pyplot as plt
from ILearner import LIFT
from sklearn.model_selection import train_test_split

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim
import pickle
import re
import nltk
import sys
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
labels = []
labels_inv = []

ordinals = ['first',
 'second',
 'third',
 'fourth',
 'fifth',
 'sixth',
 'seventh',
 'eighth',
 'ninth',
 'tenth',
 'eleventh',
 'twelfth',
 'thirteenth',
 'fourteenth',
 'fifteenth',
 'sixteenth',
 'seventeenth',
 'eighteenth',
 'nineteenth',
 'twentieth',
 'thirtieth',
 'fortieth',
 'fiftieth',
 'sixtieth',
 'seventieth',
 'eightieth',
 'ninetieth',
 'hundredth',
 'thousandth']


def ReadLabels():
	with codecs.open(labelsPath, "r",'utf-8') as fin:
		i = 0
		for row in fin:
			labels[i] = row.strip()
			labels_inv[row.strip()] = i

def ReadTrain():
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
	with codecs.open(validationPath, "r",'utf-8') as fin:
		i = 0
		for row in fin:
			if i % 2 == 0:
				testX.append(row.strip())
			else:
				pass
			i = i + 1

def getVenue(venue, d=dict()):
	tmp = d.get(venue)
	if tmp:
		return tmp
	tmp = venue
	venue = venue.lower()
	#Remove Roman numerals, and artifacts like '12.'
	venue = re.sub(r'M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})', '', venue)
	venue = re.sub(r'\d+\.', '', venue)
	#Remove numbers
	venue = re.sub(r' \d+ ', '', venue)
	#Remove years
	venue = re.sub(r'\'\d{2}', '', venue)
	venue = re.sub(r'\d{4}', '', venue)
	#Remove ordinals
	venue = re.sub(r'\d+(st|nd|rd|th)', '', venue)
	venue = venue.split()
	venue = [x for x in venue if not any([o in x for o in ordinals])]
	venue = ' '.join(venue)
	#Remove stuff in brackets, and other boilerplate details
	f = venue.find('(')
	if f > 0:
		venue = venue[:f]
	f = venue.find(':')
	if f > 0:
		venue = venue[:f]
	f = venue.find(';')
	if f > 0:
		venue = venue[:f]
	f = venue.find('vol.')
	if f > 0:
		venue = venue[:f]
	f = venue.find('volume')
	if f > 0:
		venue = venue[:f]
	f = venue.find('part')
	if f > 0:
		venue = venue[:f]
	d[tmp] = venue
	return venue

def getData(fileName):
	papers = dict()
	with codecs.open(fileName, 'r',encoding='utf-8') as f:
	#with open(fileName, 'r',encoding='utf-8') as f:
		l = f.readline()
		count = 1
		while l:
			#Get data of a single paper.
			paperTitle = ''
			authors = []
			year = -1
			venue = ''
			index = ''
			refs = set()
			abstract = ''

			while l and l != '\n':
				tmp = l
				l = f.readline()

				#Extract multi-line stuff
				while l and l != '\n' and (not(l.startswith('#'))):
					tmp += (' ' + l.strip())
					l = f.readline()

				#Remove non-ASCII characters.
				#tmp = re.sub(r'[^\x00-\x7F]+', ' ', tmp)

				if tmp.startswith('#*'): # --- paperTitle
					paperTitle = tmp[2:].strip()
					# print 'paperTitle: %s'%paperTitle
				elif tmp.startswith('#@'): # --- Authors
					al = tmp[2:].split(',')
					al = list(map(unicode.strip, al))
					authors = al
					# print 'Authors:', al
				elif tmp.startswith('#t'): # ---- Year
					year = int(tmp[2:])
					# print 'Year:', year
				elif tmp.startswith(u'#c'): #  --- publication venue
					venue = tmp[2:].strip()
					venue = getVenue(venue)
					# print 'Venue:', venue
				elif tmp.startswith('#index'): # 00---- index id of this paper
					index = tmp[6:].strip()
					# print 'Index:', index
				elif tmp.startswith('#%'): # ---- the id of references of this paper
					ref = tmp[2:].strip()
					refs.add(ref)
				elif tmp.startswith('#!'): # --- Abstract
					abstract = tmp[2:].strip()
					# print 'Abstract:', abstract

			if count % 100000 == 0:
				print('Parsed %d papers' % count)
			count += 1
			if paperTitle != '' and authors != [] and index != '':
				papers[index] = (paperTitle, authors, year, venue, refs, abstract)
			l = f.readline()

	return papers

def getLDAModel(paperData, numTopics=25, numPasses=2):
	# create English stop words list
	en_stop = stopwords.words('english')

	# Create p_stemmer of class PorterStemmer
	p_stemmer = PorterStemmer()

	#Get Doc List
	doc_set = [paperData[paper][0] + ' ' + paperData[paper][5] for paper in paperData]

	#Save memory
	del paperData

	print('%s: Got data' % datetime.datetime.now())

	# list for tokenized documents in loop
	texts = []

	# loop through document list
	count = 0
	for i in doc_set:
		# clean and tokenize document string
		raw = i.lower()
		tokens = nltk.word_tokenize(raw)
		# remove stop words from tokens
		stopped_tokens = [i for i in tokens if not i in en_stop]
		# stem tokens
		stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
		# add tokens to list
		texts.append(filter(lambda x: len(x) > 1, stemmed_tokens))
		count += 1
		if count % 100000 == 0:
			print('%s: Stemmed %d papers' % (datetime.datetime.now(),count))

	print('%s: Stemmed all papers!' % datetime.datetime.now())
	
	#Save memory
	del doc_set
	# turn our tokenized documents into a id <-> term dictionary
	dictionary = corpora.Dictionary(texts)
	print('%s: turned our tokenized documents into a id <-> term dictionary' % datetime.datetime.now())
	with open('dictionary.pkl', 'wb') as f:
		pickle.dump(dictionary, f)

	# convert tokenized documents into a document-term matrix
	corpus = [dictionary.doc2bow(text) for text in texts]
	print('%s: converted tokenized documents into a document-term matrix' % datetime.datetime.now())

	#Save memory
	del texts

	# generate LDA model - Multi Core
	ldamodel = gensim.models.ldamulticore.LdaMulticore(corpus, num_topics=numTopics, 
		id2word = dictionary, passes=numPasses)

	print('%s: Model trained.' % datetime.datetime.now())

	ldamodel.save('LDAModel.pkl')
	print('%s: Model saved.' % datetime.datetime.now())

	return ldamodel

def getTopics(paperIdx,model):
	paperText = preProcess(paperData[paperIdx][0] + ' ' + paperData[paperIdx][5])
	return model[paperText]

def preProcess(paperText):
	raw = paperText.lower()
	tokens = nltk.word_tokenize(raw)
	# remove stop words from tokens
	stopped_tokens = [i for i in tokens if not i in en_stop]
	# stem tokens
	stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
	# add tokens to list
	tokens = filter(lambda x: len(x) > 1, stemmed_tokens)
	return dictionary.doc2bow(tokens)

def Preprocess():
	paperData = getData(paperPath)

	print('%s: Loaded data' % datetime.datetime.now())
	m = getLDAModel(paperData, 100) 
	print(m)

	en_stop =  stopwords.words('english')
	model = gensim.models.ldamulticore.LdaMulticore.load('LDAModel.pkl')
	dictionary = pickle.load(open('dictionary.pkl', 'rb'))

	p_stemmer = PorterStemmer()

	print('Done loading stuff!')
	d = dict()
	i = 0
	for paperIdx in paperData:
		d[paperIdx] = getTopics(paperIdx,model)
		i += 1
		if i % 1000 == 0:
			print('Done with %d papers!'%i)
	with open('paperToTopics.pkl', 'wb') as f:
		pickle.dump(d, f)


def reformatData(X,Y):
	"""
	X - Vector of Name
	Y - Vector of Vec3sz of interests
	"""
	return X,Y


def TrainAndOutput():
	#Train:
	X_train, X_test, y_train, y_test = train_test_split(trainX, trainY, test_size=0.3, random_state=0)
	xtrain, ytrain = reformatData(X_train,X_test)
	xtest, ytest = reformatData(X_test,y_test)


	model = LIFT(0.2,range(len(labels)))
	model.train(xtrain,ytrain)
	print("score: %r\n" % (model.score(xtest,ytest)))

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


def main():
	Preprocess()
	#task3.ParsePaperTxt()
	#ReadLabels()
	#ReadTrain()
	#ReadValidation()
	#TrainAndOutput()
	#analisis()

if __name__ == "__main__":
	main()