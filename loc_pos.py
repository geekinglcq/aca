import re
import codecs
import utility
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
        self.pos_p = re.compile(r'|'.join([ r'\b'+i+r'\b' for i in self.pos_list]).replace(r'.', r'\.'))
        # self.pos_p = set(self.pos_list)
        self.year_p = re.compile(r'((?:19|20)[0-9]{2})')
        self.loc_p = re.compile('|'.join([r'\b'+i+r'\b' for i in self.loc_list]))
    def check_pos(self, html_text, index):
        le = max(index - 2, 0)
        ri = min(index + 2, len(html_text)) + 1
        for i in range(le, ri):
            if 'position' in html_text[i] or '职' in html_text[i] \
            or 'title' in html_text[i]:
                return True

    def pos_guess(self, html_text):
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
                poss.extend(self.pos_p.findall(html_text[i]))
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
        return poss
    def predict_pos(self, data, html):
        for i, r in data.iterrows():
            text = utility.get_clean_text(html[r['id']])
            pos = self.pos_guess(text)
            data.set_value(i, 'position', pos)

    def loc_guess(self, html_text):
        html_text = html_text.split('\n')
        locs = []
        for i in html_text:
            locs.extend(self.loc_p.findall(i))
        return locs
        
    def predict_loc(self, data, html):
        for i, r in data.iterrows():
            loc = self.loc_guess(html[r['id']])
            data.set_value(i, 'location', loc)
