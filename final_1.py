# -*- coding: utf-8 -*-

import json
import face
import first
import codecs
import loc_pos
import crawler
import data_io as dio 
import pagehome as ph
import gender_name as gn

raw_data_path = './task1/validation.txt'
model_path = './model/temp.dat'
search_res = './data/search_res.json'
def main():
    data = dio.read_task1(raw_data_path)
    res = crawler.multi_thread_get_search_page(data, threads_num=20)
    with codecs.open(search_res, 'w', 'utf8') as f:
        json.dump(res, f)
    model = ph.load_homepage_model(model_path)
    ph.predict_homepage(model, data, res)
    crawler.store_multi_thread(data, threads=20, prefix='./final/')
    html = first.get_homepage_html(data, prefix='./final/')
    pic_urls = first.data_pic_url(data, html)
    succ = crawler.multi_thread_download_image(pic_urls, threads_num=20)
    pic_ans = face.filter_pic(succ)
    face.predict_pic(data, pic_ans)
    gender = gn.gender_guesser()
    gender.predict_gender(data)
    first.predict_email(data, html)
    lp_guesser = loc_pos.locpos_guesser()
    lp_guesser.predict_loc(data, html)
    lp_guesser.predict_pos(data, html)
