# -*- coding: utf-8 -*-
import time
import json
# import face
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
head_succ = './data/head_succ.json'
temp_data = './data/temp_data_store.dat'
final_output = './output/task1_ans.txt'
def main():
    # time_stamp = time.time()
    # data = dio.read_task1(raw_data_path)
    # res = crawler.multi_thread_get_search_page(data, threads_num=20)
    # with codecs.open(search_res, 'w', 'utf8') as f:
    #     json.dump(res, f)

    # print('download search page cost %s'%(time.time() - time_stamp))
    # time_stamp = time.time()

    # model = ph.load_homepage_model(model_path)
    # ph.predict_homepage(model, data, res)
    # print('judge homepages cost %s'%(time.time() - time_stamp))
    # time_stamp = time.time()

    # crawler.store_multi_thread(data, threads=20, prefix='./final/')
    data = dio.read_former_task1_ans('./submit/t1_924_e3pic3hfv5.txt')
    html = first.get_homepage_html(data, prefix='./ttt/')
    print('download homepages cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()

    pic_urls = first.data_pic_url(data, html)
    succ = crawler.multi_thread_download_image(pic_urls, threads_num=10)
    with codecs.open(head_succ, 'w', 'utf-8') as f:
        json.dump(succ, f)
    print('judge head pics cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()

    gender = gn.gender_guesser()
    gender.predict_gender(data)
    first.predict_email(data, html)
    lp_guesser = loc_pos.locpos_guesser()
    lp_guesser.predict_loc(data, html)
    lp_guesser.predict_pos(data, html)
    print('judge gender location position cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()
    ## To use face.py to detect face, we need activate tensorflow first
    # first.generat_ans_file(data, True, temp_data)
    # data = dio.read_former_task1_ans(temp_data)
    # succ = json.load(head_succ)
    # pic_ans = face.filter_pic(succ)
    # face.predict_pic(data, pic_ans)
    # first.generat_ans_file(final_output)

