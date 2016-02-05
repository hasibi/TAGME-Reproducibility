"""
Methods to annotate queries with TagMe API.

@author: Faegheh Hasibi
"""

import argparse

import requests

from nordlys.entity.entity import Entity
from nordlys.tagme.test_coll import read_tagme_queries, read_yerd_queries, read_erd_queries
from nordlys.wikipedia.utils import WikipediaUtils
from nordlys.tagme import econfig


class DexterAPI(object):
    ANNOT_DEXTER_URI = "http://dexterdemo.isti.cnr.it:8080/dexter-webapp/api/rest/annotate?min-conf=0"
    DESC_DEXTER_URI = "http://dexterdemo.isti.cnr.it:8080/dexter-webapp/api/rest/get-desc"

    def __init__(self):
        self.entity = Entity()
        self.id_title_dict = {}

    def ask_dexter_query(self, query):
        """Sends queries to Dexter Api."""
        data = {'dsb': "tagme", 'n': "50", 'debug': "false", 'format': "text", 'text': query}
        res = requests.post(self.ANNOT_DEXTER_URI, data).json()
        res['query'] = query
        return res

    def ask_title(self, page_id):
        """Sends page id to the API and get the page title."""
        if page_id not in self.id_title_dict:
            req = "?id="+ str(page_id) + "&title-only=true"
            res = requests.get(self.DESC_DEXTER_URI +req).json()
            title = res.get('title', "")
            wiki_uri = WikipediaUtils.wiki_title_to_uri(title.encode("utf-8"))
            self.id_title_dict[page_id] = wiki_uri
        return self.id_title_dict[page_id]

    def aks_dexter_queries(self, queries, out_file, qid_th=None):
        """
        Sends queries to Dexter Api and writes them in a json file.

        :param queries: dictionary {qid: query, ...}
        :param json_file: The file to write json output
        """
        print "Getting resutls from Tagme ..."
        # responses = {}
        out_str = ""
        open(out_file, "w").close()
        out = open(out_file, "a")
        i = 0
        for qid in sorted(queries, key=lambda item: int(item) if item.isdigit() else item):
            if qid_th and qid_th.isdigit() and int(qid) < int(qid_th):
                continue
            query = queries[qid]
            print qid, query
            tagme_res = self.ask_dexter_query(query)
            out_str += self.__to_str(qid, tagme_res)
            out.write(out_str)
            out_str = ""
            i += 1
            if i % 100 == 0:
                # out.write(out_str)
                print i, "th query processed ...."
                print "items ins the page-id cache:", len(self.id_title_dict)
                self.id_title_dict = {}
                # out_str = ""
        out.write(out_str)
        # json.dump(responses, open(out_file, "w"), indent=4, sort_keys=True)
        print "Dexter results: " + out_file
        # return responses

    def __to_str(self, qid, response):
        """
        Output format:
        qid, score, wiki-uri, mention, page-id, start, end, linkProbability, linkFrequency, documentFrequency,
        entityFrequency, commonness

        :param qid:
        :param response:
        :return:
        """
        none_str = "*NONE*"
        out_str = ""
        for annot in response['spots']:
            wiki_uri = self.ask_title(annot.get('entity', none_str))
            if wiki_uri is None:
                continue
            qid_str = str(qid) + "\t" + str(annot.get('score', none_str)) + "\t" + wiki_uri + "\t" + \
                       annot.get('mention', none_str) + "\t" + str(annot.get('entity', none_str)) + "\t" + \
                       str(annot.get('start', none_str)) + "\t" + str(annot.get('end', none_str)) + "\t"+\
                       str(annot.get('linkProbability', none_str)) + "\t" + str(annot.get('linkFrequency', none_str)) + "\t" +\
                       str(annot.get('documentFrequency', none_str)) + "\t" + str(annot.get('entityFrequency', none_str)) + "\t" +\
                       str(annot.get('commonness', none_str)) + "\n"
            out_str += qid_str
        return out_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-th", "--threshold", help="rho score threshold", type=float, default=0)
    parser.add_argument("-qid", help="annotates queries from this qid", type=str)
    parser.add_argument("-data", help="Data set name", choices=['ysqle', 'ysqle-tagme', 'tagme', 'tagme-test',
                                                                'wiki-annot30', 'wiki-disamb30'])
    args = parser.parse_args()

    if args.data == "tagme":
        queries = read_erd_queries(process=False)
    elif args.data == "ysqle-tagme":
        queries = read_yerd_queries(process=False)
    elif args.data == "wiki-annot30":
        queries = read_tagme_queries(econfig.WIKI_ANNOT30_SNIPPET, process=False)
    elif args.data == "wiki-disamb30":
        queries = read_tagme_queries(econfig.WIKI_DISAMB30_SNIPPET, process=False)

    # asks tagMe and creates output file
    qid_str = "_" + args.qid if args.qid else ""
    out_file = econfig.OUTPUT_DIR + "/eval/" + args.data + "_dexter" + qid_str + ".eval"
    tagme = DexterAPI()
    tagme.aks_dexter_queries(queries, out_file, qid_th=args.qid)


if __name__ == '__main__':
    main()