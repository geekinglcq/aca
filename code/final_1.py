# -*- coding: utf-8 -*-
import time
import json
# import face
import first
import codecs
import loc_pos
import crawler
import logging
import data_io as dio 
import pg2 as ph
import gender_name as gn

raw_data_path = './task1/a.txt'
model_path = './model/good_model.dat'
search_res = './output/search_res.json'
html_res = './output/html_res.json'
head_succ = './output/head_succ.json'
temp_data = './output/temp_data_store.dat'

final_output = './output/task1_ans.txt'
def main():
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename='./t1_run.log', level=logging.INFO, format=FORMAT)
    time_stamp = time.time()
    data = dio.read_task1(raw_data_path)
    res = crawler.multi_thread_get_search_page(data, threads_num=1)
    with codecs.open(search_res, 'w', 'utf8') as f:
        json.dump(res, f)

    logging.info('download search page cost %s'%(time.time() - time_stamp))
    
    time_stamp = time.time()
    res = json.load(codecs.open(search_res, 'r', 'utf-8'))
    model = ph.load_homepage_model(model_path)
    ph.predict_homepage(model, data, res)
    logging.info('judge homepages cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()
    
    crawler.store_multi_thread(data, threads=1, prefix='./final/')
    crawler.store_d_html_text_multi(data, prefix='./final/', threads_num=10)
    html = first.get_homepage_html(data, prefix='./final/')
    with codecs.open(html_res, 'w', 'utf8') as f:
        json.dump(html, f)
    html = json.load(codecs.open(html_res, 'r', 'utf-8'))
    logging.info('download homepages cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()
    
    pic_urls = first.data_pic_url(data, html)
    succ = crawler.multi_thread_download_image(pic_urls, threads_num=1)
    with codecs.open(head_succ, 'w', 'utf-8') as f:
        json.dump(succ, f)
    logging.info('judge head pics cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()
    
    gender = gn.gender_guesser()
    gender.predict_gender(data)
    
    first.predict_email(data, html)

    logging.info('predict email cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()

    lp_guesser = loc_pos.locpos_guesser()
    lp_guesser.predict_loc(data, html)
    lp_guesser.predict_pos(data, html)
    logging.info('judge gender location position cost %s'%(time.time() - time_stamp))
    time_stamp = time.time()
    ## To use face.py to detect face, we need activate tensorflow first
    # first.generat_ans_file(data, True, temp_data)
    # data = dio.read_former_task1_ans(temp_data)
    # succ = json.load(head_succ)
    # pic_ans = face.filter_pic(succ)
    # face.predict_pic(data, pic_ans)
    first.generat_ans_file(data, True, final_output)

if __name__ == '__main__':
    main()