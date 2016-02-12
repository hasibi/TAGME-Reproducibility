"""
Reads surface forms extracted from titles, redirects, and anchors and merge them into a single json file,
which can be directly imported to Mongodb using this command:

 mongoimport --db <db_name> --collection surfaceforms_wiki_YYYYMMDD --file <path_to_json_file> --jsonArray

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""
import argparse

import os
import json
from urllib import unquote
from nordlys.storage.mongo import Mongo
from nordlys.wikipedia.utils import WikipediaUtils


class Merger(object):

    def __init__(self):
        self.all_sfs = {}

    def merge_all(self, titles_file, redirects_file, anchors_file, out_file):
        self.add_anchors(anchors_file)
        self.add_titles(titles_file)
        self.add_redirects(redirects_file)

        # Converting all surface forms to mongo format
        print "Converting to mongodb format ..."
        sf_mongo_entries = []
        i = 0
        for sf, en_sources in self.all_sfs.iteritems():
            escaped_sf = Mongo.escape(sf)
            entry = {"_id": escaped_sf}
            for source, en in en_sources.iteritems():
                entry[source] = en
            sf_mongo_entries.append(entry)
            i += 1
            if i % 1000000 == 0:
                print "processes", i, "the surface form"
        print "writing to json file ..."
        json.dump(sf_mongo_entries, open(out_file, "w"), indent=4, sort_keys=True)

    def __add_to_dict(self, sf, pred, en, count=1):
        if sf not in self.all_sfs:
            self.all_sfs[sf] = {}
        if pred not in self.all_sfs[sf]:
            self.all_sfs[sf][pred] = {en: count}
        else:
            self.all_sfs[sf][pred][en] = count

    # ============== ANCHORS ==============

    def add_anchors(self, anchor_file):
        print "Adding anchors ..."
        i = 0
        infile = open(anchor_file, "r")
        for line in infile:
            # print line
            cols = line.strip().split("\t")
            sf = cols[0].strip()
            count = int(cols[2])
            wiki_uri = WikipediaUtils.wiki_title_to_uri(unquote(cols[1].strip()))
            self.__add_to_dict(sf, "anchor", wiki_uri, count)
            i += 1
            if i % 1000000 == 0:
                print "Processed", i, "th anchor!"

    # ============== REDIRECTS ==============

    def add_redirects(self, redirect_file):
        """Adds redirect pages to the surface form dictionary."""
        print "Adding redirects ..."
        redirects = open(redirect_file, "r")
        count = 0
        for line in redirects:
            cols = line.strip().split("\t")
            sf = cols[0].strip().lower()
            wiki_uri = WikipediaUtils.wiki_title_to_uri(cols[1].strip())
            # print sf, wiki_uri
            self.__add_to_dict(sf, "redirect", wiki_uri)
            count += 1
            if count % 1000000 == 0:
                print "Processed ", count, "th redirects."

    # ============== TITLES ==============

    def add_titles(self, title_file):
        """Adds titles and title name variants to the surface form dictionary."""
        print "Adding titles ..."
        redirects = open(title_file, "r")
        count = 0
        for line in redirects:
            cols = line.strip().split("\t")
            title = unquote(cols[1].strip())
            wiki_uri = WikipediaUtils.wiki_title_to_uri(title)
            self.__add_to_dict(title.lower(), "title", wiki_uri)
            title_nv = self.__title_nv(title)
            if (title_nv != title) and (title_nv.strip() != ""):
                self.__add_to_dict(title_nv.lower(), "title-nv", wiki_uri)
            count += 1
            if count % 1000000 == 0:
                print "Processed ", count, "th titles."

    @staticmethod
    def __title_nv(title):
        """Removes all letters after "(" and "," from page title."""
        p_pos = title.find("(")
        title_nv = title[:p_pos] if p_pos != -1 else title
        c_pos = title.find(",")
        title_nv = title[:c_pos] if c_pos != -1 else title_nv
        return title_nv.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-anchors", help="Path to anchor file")
    parser.add_argument("-redirects", help="Path to redirect file")
    parser.add_argument("-titles", help="Path to page-title file")
    parser.add_argument("-outputdir", help="Path to output directory")
    args = parser.parse_args()


    # Merges titles, redirects, and anchors
    merger = Merger()
    merger.merge_all(args.titles, args.redirects, args.anchors, args.outputdir + "/sf_dict_mongo.json")

if __name__ == "__main__":
    main()