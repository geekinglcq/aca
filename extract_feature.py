from __future__ import division
import json
import codecs


def compute_author_hindex(record,year_t = 10000):

    cite_num = []
    for v in record:
        num = 0
        for year,n in v[1].items():
            if int(float(year)) <= year_t:
                num += n
        cite_num.append(num)
    cite_num.sort(reverse=True)
    h_index = 0
    for i,v in enumerate(cite_num):
        if i+1 > v:
            h_index = i
            break
    #h_index = 0 if h_index < 0 else h_index

    return h_index

def compute_author_citation(record,year=10000,first=-1):
    citation = 0
    for v in record:
        if v[2] != first:
            for y,n in v[1].items():
                if int(float(y)) <= year:
                    citation += n
    return citation

def compute_author_papers(record,year=10000,first=-1):

    num = 0
    for v in record:
        if v[2] != first:
            if v[3] <= year:
                num += 1
    return num

def compute_author_max_single_paper_citations(record):

    cite_num = [0]
    for v in record:
        num = 0
        for year,n in v[1].items():
            num += n
        cite_num.append(num)

    return max(cite_num)

def compute_author_age(record):

    publish_year = [0]
    for v in record:
        publish_year.append(float(int(v[3])))

    return max(publish_year)-min(publish_year)+1

def compute_author_mean_citations_per_paper(record,year):
    citations = compute_author_citation(record,year)
    paper_published = compute_author_papers(record,year)
    paper_published = 1 if paper_published == 0 else paper_published
    return (citations/paper_published)

def compute_author_mean_citations_per_year(record):
    dur = compute_author_age(record)
    citations = compute_author_citation(record,10000)
    return (citations/dur)

def compute_author_mean_citation_rank():
    with codecs.open("./out_data/author_feature.json","r","utf-8") as fid:
        author_feature = json.load(fid)

    citations_per_year_list = []
    for author in author_feature.keys():
        citations_per_year_list.append(author_feature[author]['author_mean_citations_per_year'])
    length = len(citations_per_year_list)

    citations_per_year_list.sort(reverse=True)
    for author in author_feature.keys():
        indx = citations_per_year_list.index(author_feature[author]['author_mean_citations_per_year'])
        author_feature[author].setdefault('author_mean_citation_rank',indx/length)

    with codecs.open("./out_data/author_feature.json","w","utf-8") as fid:
        json.dump(author_feature,fid,ensure_ascii=False)

def compute_feature():
    with codecs.open("./input_data/au_p","r","utf-8") as fid:
        author_record = json.load(fid)

        author_feature = {}
    for author,record in author_record.items():
        author_feature.setdefault(author,{})
        author_feature[author].setdefault('author_hindex_2013',compute_author_hindex(record,year_t=2013))
        author_feature[author].setdefault('author_hindex_2013_2011', compute_author_hindex(record,year_t=2013)-compute_author_hindex(record,year_t=2011))
        #author_feature[author].setdefault('hindex_2013', compute_author_hindex(record,year_t=2013))
        author_feature[author].setdefault('author_citiation_count',compute_author_citation(record,year=10000,first=-1))
        author_feature[author].setdefault('author_key_citiation_count', compute_author_citation(record,year=10000,first=0))
        author_feature[author].setdefault('author_citiation_count_2011', compute_author_citation(record,year=2011,first=-1))
        author_feature[author].setdefault('author_citiation_count_2012', compute_author_citation(record,year=2012,first=-1))
        author_feature[author].setdefault('author_citiation_count_2013',compute_author_citation(record,year=2013,first=-1))
        author_feature[author].setdefault('author_key_citiation_count_2011', compute_author_citation(record,year=2011,first=0))
        author_feature[author].setdefault('author_key_citiation_count_2012', compute_author_citation(record,year=2012,first=0))
        author_feature[author].setdefault('author_key_citiation_count_2013',compute_author_citation(record,year=2013,first=0))
        author_feature[author].setdefault('author_citiations_delta_01',compute_author_citation(record,year=2013,first=-1)-compute_author_citation(record,year=2012,first=-1))
        author_feature[author].setdefault('author_key_citiations_delta_01',compute_author_citation(record,year=2013,first=0)-compute_author_citation(record,year=2012,first=0))

        author_feature[author].setdefault('author_mean_citations_per_paper',compute_author_mean_citations_per_paper(record,10000))
        author_feature[author].setdefault('author_mean_citations_per_paper_delta',compute_author_mean_citations_per_paper(record,2013)-compute_author_mean_citations_per_paper(record,2011))
        author_feature[author].setdefault('author_mean_citations_per_year',compute_author_mean_citations_per_year(record))
        author_feature[author].setdefault('author_papers',compute_author_papers(record,year=2013,first=-1))
        author_feature[author].setdefault('author_papers_delta',compute_author_papers(record,year=2013,first=-1)-compute_author_papers(record,year=2011,first=-1))
        author_feature[author].setdefault('author_max_single_paper_citations',compute_author_max_single_paper_citations(record))
        author_feature[author].setdefault('author_age',compute_author_age(record))

    with codecs.open("./out_data/author_feature.json","w","utf-8") as fid:
        json.dump(author_feature,fid,ensure_ascii=False)


if __name__ == "__main__":
    #compute_feature()
    compute_author_mean_citation_rank()






