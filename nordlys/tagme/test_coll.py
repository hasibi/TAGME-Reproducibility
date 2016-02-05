"""
Reads queries from test collections

@author: Faegheh Hasibi
"""

import csv
from nordlys.tagme import econfig
from nordlys.tagme.query import Query


def read_yerd_queries(ysqle_erd_file=econfig.YSQLE_ERD, process=True):
    """
    Reads queries from Erd query file.

    :return dictionary {query_id : query_content}
    """
    queries = {}
    with open(ysqle_erd_file, 'rb') as ysqle_erd:
        reader = csv.DictReader(ysqle_erd, delimiter="\t", quoting=csv.QUOTE_NONE)

        for line in reader:
            qid = line['qid']
            query = line['query']
            if process:
                queries[qid] = Query.preprocess(query.strip()).lower()
            else:
                queries[qid] = query.strip()
    print "Number of queries:", len(queries)
    return queries


def read_erd_queries(erd_q_file=econfig.ERD_QUERY, process=True):
    """
    Reads queries from Erd query file.

    :return dictionary {query_id : query_content}
    """
    queries = {}
    q_file = open(erd_q_file, "r")
    for line in q_file:
        line = line.split("\t")
        query_id = line[0].strip()
        if process:
            query_content = Query.preprocess(line[-1].strip()).lower()
        else:
            query_content = line[-1].strip()
        queries[query_id] = query_content
    q_file.close()
    print "Number of queries:", len(queries)
    return queries


def read_tagme_queries(dataset_file, process=True):
    """
    Reads queries from snippet file.

    :return dictionary {query_id : query_content}
    """
    queries = {}
    q_file = open(dataset_file, "r")
    for line in q_file:
        line = line.strip().split("\t")
        query_id = line[0].strip()
        if process:
            query_content = Query.preprocess(line[1].strip().lower())
        else:
            query_content = line[1].strip()
        queries[query_id] = query_content
    q_file.close()
    print "Number of queries:", len(queries)
    return queries