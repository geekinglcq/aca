import re
import codecs
import pandas as pd

from utility import get_clean_text
from pg2 import check_name_in_text
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
        self.pos_p = re.compile(r'|'.join([ r'\b'+i+r'\b' for i in self.pos_list]).replace(r'.', r'\.'))
        # self.pos_p = set(self.pos_list)
        self.year_p = re.compile(r'((?:19|20)[0-9]{2})')
        self.loc_p = re.compile('|'.join([r'\b'+i+r'\b' for i in self.loc_list]))
    def check_pos(self, html_text, name, index):
        pos_words_p = re.compile(r'[Pp]osition[^"]|职|[Tt]itle[^=>"]')
        le = max(index - 5, 0)
        ri = min(index + 5, len(html_text))
        for i in range(le, ri):
            if len(html_text[i]) <= 8:
                if i < (le + ri) / 2:
                    le = max(le - 1, 0)
                else:
                    ri = min(ri + 1, len(html_text))
        
        for i in range(le, ri):
            years = self.year_p.findall(html_text[i])
            if len(years) > 0:
                years = list(map(lambda x: int(x), years))
                if max(years) < 2017:
                    continue
            if  pos_words_p.search(html_text[i]):
                return True
            if check_name_in_text(name, html_text[i]) > 0.2:
                
                return True
            # for part_name in name.lower().split():
            #     if part_name in html_text[i].lower():
            #         return True
        return False

    def pos_guess(self, name, html_text):
        html_text = html_text.split('\n')
        poss = []
        ppp = []
        for i in range(len(html_text)):
            if 'was' not in html_text[i]:
                
                years = self.year_p.findall(html_text[i])
                if len(years) > 0:
                    years = list(map(lambda x: int(x), years))
                    if max(years) < 2017:
                        continue
                temp_pos = self.pos_p.findall(html_text[i])
                if len(temp_pos) > 0:
                    if self.check_pos(html_text, name, i):
                        poss.extend(temp_pos)
                # if len(self.pos_p.findall(html_text[i])) > 0:
                #     ppp.append((html_text[i], self.pos_p.findall(html_text[i])))    
                # items = set(re.split(r'[ ,_.-@\(\)。\r|\n]', html_text[i]))
                # candidates = list(items & self.pos_p)
                # if len(candidates) > 0:
                #     ppp.append((html_text[i], candidates))
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
        
    def predict_pos(self, data, html):
        for i, r in data.iterrows():
            text = get_clean_text(html[r['id']])
            pos = self.pos_guess(r['name'], text)
            data.set_value(i, 'position', ';'.join(pos))

    def loc_guess(self, html_text):
        html_text = html_text.split('\n')
        locs = []
        for i in html_text:
            locs.extend(self.loc_p.findall(i))
        return locs
        
    def predict_loc(self, data, html):
        for i, r in data.iterrows():
            loc = self.loc_guess(r['name'], html[r['id']])
            data.set_value(i, 'location', loc)
