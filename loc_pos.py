import re
import json
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
        self.org_loc = json.load(codecs.open('./data/org_location.json', 'r', 'utf-8'))
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

    def check_loc(self, i, name, org, html_text):
        le = max(i - 4, 0)
        ri = min(i + 4, len(html_text))
        for i in range(le, ri):
            if len(html_text[i]) <= 8:
                if i < (le + ri) / 2:
                    le = max(le - 1, 0)
                else:
                    ri = min(ri + 1, len(html_text))
        score = [0 for i in range(12)]
        for i in range(le, ri):
            line_score = self.score_one_line(html_text[i], org, name)
            for j in range(len(line_score)):
                # score[j] = score[j] + line_score[j]
                score[j] = max(score[j], line_score[j])
        score = sum(score)
        return score

    def score_one_line(self, line, org, name):
        score = []
        key_words = ['mail', 'address', 'phone', 'tel', 'fax', 'room', 'office', 'road', 'street', 'avenue']
        score.append(check_name_in_text(org, line))
        score.append(check_name_in_text(name, line))
        for i in key_words:
            if i in line.lower():
                score.append(1)
            else:
                score.append(0)
        return score

    def loc_guess(self, name, org, html_text):
        html_text = html_text.split('\n')
        locs = []
        for i, text in enumerate(html_text):
            if self.loc_p.search(text):
                if self.check_loc(i, name, org, html_text) > 3:
                    locs.extend(self.loc_p.findall(text))
        locs = list(set(locs))
        return locs
        
    def predict_loc(self, data, html):
        for i, r in data.iterrows():
            # if r['org'] in self.org_loc:
            #     data.set_value(i, 'location', self.org_loc[r['org']])
            #     continue
            loc = self.loc_guess(r['name'], r['org'], html[r['id']])
            
            if len(loc) == 1:
                data.set_value(i, 'location', loc[0])
            else:
                data.set_value(i, 'location', '')
