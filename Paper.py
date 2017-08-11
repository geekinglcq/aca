class Paper(object):
	"""description of class"""
	__wholeData = {}
	__authorData={}
	def __init__(self,index,author="",title="",time=0,journal=""):
		self.Index=index
		self.Author=author
		self.Title=title
		self.Time=time
		self.Journal=journal
		self.References=[]
		self.Referenced=[]

	@staticmethod
	def getPaperById(id):
		if not (id in Paper.__wholeData):
			Paper.__wholeData[id]=Paper(id)
		return Paper.__wholeData[id]

	@staticmethod
	def getPaperByAut(author):
		if not (author in Paper.__authorData):
			Paper.__authorData[author]=[]
		return Paper.__authorData[author]

	@staticmethod
	def addAutPaper(aut,pa):
		if not (aut in Paper.__authorData):
			Paper.__authorData[aut]=[pa]
		else:
			Paper.__authorData[aut].append(pa)

	