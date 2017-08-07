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
		if not Paper.__wholeData.has_key(id):
			Paper.__wholeData[id]=Paper(id)
		return Paper.__wholeData[id]

	@staticmethod
	def getPaperByAut(author):
		if not Paper.__authorData.has_key(author):
			Paper.__authorData[author]=[]
		return Paper.__authorData[author]

	@staticmethod
	def addAutPaper(aut,pa):
		if not Paper.__authorData.has_key(aut):
			Paper.__authorData[aut]=[pa]
		else:
			Paper.__authorData[aut].append(pa)

	