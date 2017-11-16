from __future__ import division
import networkx as nx
import json
import codecs
from collections import Counter


def create_cite_net(author_indx_citeindx):
    print ("create cite net ...")
    cite_graph = nx.Graph()
    for author in author_indx_citeindx.keys():
        for indx,citeindx in author_indx_citeindx[author].items():
            cite_graph.add_node(indx)
            for v in citeindx:
                cite_graph.add_edge(indx,v)
    return cite_graph

def find_neighbors(cite_graph):

    print ("find neighbors ....")
    indx_neighbors = {}
    for node in cite_graph.nodes():
        indx_neighbors.setdefault(node,[]).extend(list(nx.all_neighbors(cite_graph,node)))
    with codecs.open("./raw_data/indx_neighbors.json","w","utf-8") as fid:
        json.dump(indx_neighbors,fid)

if __name__ == '__main__':

    print ("create cite net ...")
    with codecs.open("./raw_data/author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)
    with codecs.open("./raw_data/author_indx_citeindx.json","r","utf-8") as fid:
        author_indx_citeindx = json.load(fid)
    cite_graph = create_cite_net(author_indx_citeindx)
    find_neighbors(cite_graph)

