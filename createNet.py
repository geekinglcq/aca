import networkx as nx 
import json
import codecs
from collections import Counter

def createRelationNetwork():

    # struct node{
    # key = author's name
    # type = 'V'/'T' ;; V means author isn't in training.txt
    # interest = []
    # }

    with codecs.open("author_cooperators.json","r","utf-8") as fid:
        author_cooperator = json.load(fid)
    with codecs.open("author_interest.json","r","utf-8") as fid:
        author_interest = json.load(fid)

    relation_net = nx.Graph()
    # graph to record the realtions between the authors

    for key,value in author_cooperator.items():
        if key in author_interest.keys():
            relation_net.add_node(key,type='T',interest = author_interest[key])
        else:
            relation_net.add_node(key,type='V',interest = [])
        value_count = Counter(value)
        # create graph , set authors' name as node, set the times that they
        # cooperated as the weighted edge

        for k,v in value_count.items():
            relation_net.add_weighted_edges_from([(key,k,v)])
    return relation_net


def expandInterest(name,relation_net):
    # input authors' name
    # expand interest 
    expand_interest = []
    cooperators = nx.all_neighbors(relation_net,name)
    for v in cooperators:
        expand_interest.extend(relation_net.node[v]['interest']*relation_net[name][v]['weight'])
    expand_interest = Counter(expand_interest).most_common(5)
    interest = []
    for i in range (len(expand_interest)):
        interest.append(expand_interest[i][0])
    relation_net.node[name]['interest'].extend(interest)
    return interest


def predict(relation_net):
    '''
    predict the validations' interest
    '''

    fid_result = codecs.open('predict2.txt','w','utf-8')

    with codecs.open('validation.txt','r','utf-8') as fid:
        for line in fid:
            if line == '\n':
                continue
            line = line.strip()
            fid_result.write(line)
            interest = []
            for v in nx.all_neighbors(relation_net,line):
                if len(relation_net.node[v]['interest']) <= 0:
                    interest.extend(expandInterest(v,relation_net)*relation_net[line][v]['weight'])
                else:
                    interest.extend(relation_net.node[v]['interest']*relation_net[line][v]['weight'])
            interest = Counter(interest).most_common(5)

            for i in range(len(interest)):
                fid_result.write('\t%s' %interest[i][0])

            for i in range(5-len(interest)):
                fid_result.write('\t0')
            fid_result.write('\n')

    fid_result.close()

if __name__ == "__main__":
    print('begin to create relation network ...')
    relation_net = createRelationNetwork()
    print('succeed creating network!\n')
    print('begin to predict ...')
    predict(relation_net)
