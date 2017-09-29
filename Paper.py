import datetime
import gc
class Paper(object):
    """description of class"""
    __wholeData = {}
    __authorData = {}

    __authorToIndexes = {}
    __IndexToGroup = {}
    __GroupData={}
    
    def __init__(self, index, author=[], title="", time=0, journal=""):
        self.Index = index
        self.Author = author
        self.Title = title
        self.Time = time
        self.Journal = journal
        self.References = []
        self.Referenced = []

    @staticmethod
    def getPaperById(id):
        if not (id in Paper.__wholeData):
            Paper.__wholeData[id] = Paper(id)
        return Paper.__wholeData[id]

    @staticmethod
    def getPaperByAut(author):
        if not (author in Paper.__authorData):
            Paper.__authorData[author] = []
        return Paper.__authorData[author]

    @staticmethod
    def addAutPaper(aut, pa):
        if not (aut in Paper.__authorData):
            Paper.__authorData[aut] = [pa]
        else:
            Paper.__authorData[aut].append(pa)

    @staticmethod
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

    @staticmethod
    def __merge(ids):
        a = len(Paper.__wholeData)
        b = len(Paper.__GroupData)
        c=0
        for id in ids:
            p = Paper.getPaperById(id)
            Paper.__IndexToGroup[id]=a+b
            c=c+len(p.Referenced)
        Paper.__GroupData[a+b] = c


    @staticmethod
    def MergePaper():
        N = len(Paper.__wholeData)
        Removed = 0
        GroupCount = 0
        for i in range(N):
            if i % 100000 == 0:
                print("%s   Merge At %d" % (datetime.datetime.now(),i))
            if i in Paper.__IndexToGroup:
                continue
            auts = Paper.__wholeData[i].Author
            s = set()
            f = True
            for aut in auts:
                t = Paper.getPaperByAut(aut)
                ids = [p.Index for p in t]
                if f:
                    f = False
                    s = set(ids)
                else:
                    s.intersection_update(ids)
            t = set()
            for id in s:
                p = Paper.getPaperById(id)
                if len(p.Author) != len(auts):
                    t.add(id)
            s.difference_update(t)
            Paper.__merge(s)
            Removed = Removed + len(s)
            GroupCount = GroupCount + 1
        Paper.OptimizeMem()
        print("TotalRemoved: %d in %d Group(s)" % (Removed,GroupCount))
       
    @staticmethod
    def OptimizeMem():
        for k,v in Paper.__authorData.items():
            Paper.__authorToIndexes[k] = [p.Index for p in v]
        del(Paper.__authorData)
        print("%s Delete author data" % (datetime.datetime.now()))

        id=0
        while id in Paper.__wholeData:
            if not id in Paper.__IndexToGroup:
                Paper.__IndexToGroup[id]=id
            id = id+1
        del(Paper.__wholeData)
        print("%s Delete whole data" % (datetime.datetime.now()))
        gc.collect()

    @staticmethod
    def RemoveAllData():
        del(Paper.__authorData)
        del(Paper.__wholeData)
        del(Paper.__authorToIndexes)
        del(Paper.__IndexToGroup   )
        del(Paper.__GroupData      )
        gc.collect()
