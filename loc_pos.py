import re
import codecs
import pandas as pd

class locpos_guesser():
    """
    Guess one's location and position with simple html text
    """

    def __init__(self):
        self.load_data()
    
    def load_data(self):
        self.pos_list = []
        self.loc_list = []
        for line in codecs.open('./data/position.txt', 'r', 'utf-8'):
            self.pos_list.append(line.strip())
        for line in codecs.open('./data/location.txt', 'r', 'utf-8'):
            self.loc_list.append(line.strip())
        self.pos_p = re.compile(r'|'.join(self.pos_list).replace(r'.', r'\.'))
        self.loc_p = re.compile('|'.join(self.loc_list))
    def pos_guess(self, html_text):
        poss = []
        for i in html_text:
            poss.extend(self.pos_p.findall(i))
        poss = list(set(poss))
        sub_filter = {}
        for i in poss:
            sub_filter[i] = True
        for i in poss:
            for j in poss:
                if i != j and i in j:
                    sub_filter[i] = False
        poss = []
        for i in sub_filter:
            if sub_filter[i]:
                poss.append(i)
        return poss
    
    def loc_guess(self, html_text):
        locs = []
        for i in html_text:
            locs.extend(self.loc_p.findall(i))
        return locs
        