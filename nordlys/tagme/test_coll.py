"""
Reads queries from test collections

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import csv
from nordlys.tagme import config


def read_yerd_queries(y_erd_file=config.Y_ERD):
    """
    Reads queries from Erd query file.

    :return dictionary {query_id : query_content}
    """
    queries = {}
    with open(y_erd_file, 'rb') as y_erd:
        reader = csv.DictReader(y_erd, delimiter="\t", quoting=csv.QUOTE_NONE)

        for line in reader:
            qid = line['qid']
            query = line['query']
            queries[qid] = query.strip()
    print "Number of queries:", len(queries)
    return queries


def read_erd_queries(erd_q_file=config.ERD_QUERY):
    """
    Reads queries from Erd query file.

    :return dictionary {qid : query}
    """
    queries = {}
    q_file = open(erd_q_file, "r")
    for line in q_file:
        line = line.split("\t")
        query_id = line[0].strip()
        query = line[-1].strip()
        queries[query_id] = query
    q_file.close()
    print "Number of queries:", len(queries)
    return queries


def read_tagme_queries(dataset_file):
    """
    Reads queries from snippet file.

    :return dictionary {qid : query}
    """
    queries = {}
    q_file = open(dataset_file, "r")
    for line in q_file:
        line = line.strip().split("\t")
        query_id = line[0].strip()
        query = line[1].strip()
        queries[query_id] = query
    q_file.close()
    print "Number of queries:", len(queries)
    return queries