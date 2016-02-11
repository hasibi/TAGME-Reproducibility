"""
Methods to annotate queries with TagMe API.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import argparse
import requests
from nordlys.config import OUTPUT_DIR
from nordlys.tagme import config
from nordlys.tagme.test_coll import read_erd_queries, read_yerd_queries, read_tagme_queries
from nordlys.wikipedia.utils import WikipediaUtils


class TagmeAPI(object):
    TAGME_URI = "http://tagme.di.unipi.it/tag"
    NONE = "*NONE*"

    def __init__(self, key):
        self.key = key

    def ask_tagme_query(self, query):
        """Sends queries to Tagme Api."""
        data = {'key': self.key, 'lang': "en", 'text': query}
        res = requests.post(self.TAGME_URI, data).json()
        res['query'] = query
        return res

    def aks_tagme_queries(self, queries, out_file):
        """
        Sends queries to Tagme Api and writes them in a json file.

        :param queries: dictionary {qid: query, ...}
        :param out_file: The file to write the output
        """
        print "Getting results from Tagme ..."
        out_str = ""
        open(out_file, "w").close()
        out = open(out_file, "a")
        i = 0
        for qid in sorted(queries):
            query = queries[qid]
            print "[" + qid + "]", query
            tagme_res = self.ask_tagme_query(query)
            out_str += self.__to_str(qid, tagme_res)
            # responses[qid] = tagme_res
            i += 1
            if i % 1000 == 0:
                out.write(out_str)
                print "until qid:", qid
                out_str = ""
        out.write(out_str)
        print "TagMe results: " + out_file

    def __to_str(self, qid, response):
        """
        Output format:
        qid, score, wiki-uri, mention, page-id, start, end
        """
        out_str = ""
        for annot in response['annotations']:
            title = str(annot.get('title', TagmeAPI.NONE))
            page_id = str(annot.get('id', TagmeAPI.NONE))
            wiki_uri = self.__get_uri_from_title(title)
            out_str += str(qid) + "\t" + str(annot.get('rho', TagmeAPI.NONE)) + "\t" + wiki_uri + "\t" + \
                       annot.get('spot', TagmeAPI.NONE) + "\t" + page_id + "\t" + \
                       str(annot.get('start', TagmeAPI.NONE)) + "\t" + str(annot.get('end', TagmeAPI.NONE)) + "\n"
        return out_str

    def __get_uri_from_title(self, title):
        return WikipediaUtils.wiki_title_to_uri(title) if title != TagmeAPI.NONE else TagmeAPI.NONE


def main():
    key = "ABgST34GTQoo89912"  # To be taken from TAGME authors

    parser = argparse.ArgumentParser()
    parser.add_argument("-data", help="Data set name", choices=['y-erd', 'erd-dev', 'wiki-annot30', 'wiki-disamb30'])
    args = parser.parse_args()

    if args.data == "erd-dev":
        queries = read_erd_queries()
    elif args.data == "y-erd":
        queries = read_yerd_queries()
    elif args.data == "wiki-annot30":
        queries = read_tagme_queries(config.WIKI_ANNOT30_SNIPPET)
    elif args.data == "wiki-disamb30":
        queries = read_tagme_queries(config.WIKI_DISAMB30_SNIPPET)

    # Asks TAGME and creates json file
    out_file = OUTPUT_DIR + "/" + args.data + "_tagmeAPI" + ".txt"
    tagme = TagmeAPI(key)
    tagme.aks_tagme_queries(queries, out_file)

if __name__ == '__main__':
    main()