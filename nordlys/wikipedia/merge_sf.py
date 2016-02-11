"""
Reads surface forms extracted from titles, redirects, and anchors and merge them into a single json file,
which can be directly imported to Mongodb using this command:

 mongoimport --db <db_name> --collection surfaceforms_wiki_YYYYMMDD --file <path_to_json_file> --jsonArray

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

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


def merge_anchors(basedir, outfile):
    """Writes all annotations into a single file."""
    open(outfile, "w").close()
    out = open(outfile, "a")
    i = 0
    for path, dirs, files in os.walk(basedir):
        for fn in sorted(files):
            if fn.endswith(".tsv"):
                with open(os.path.join(path, fn)) as in_file:
                    out.write(in_file.read())
            i += 1
            if i % 100 == 0:
                print i, "th file is added!"
                print "file:", os.path.join(path, fn)


def count_anchors(anchor_file, out_file):
    """Counts the number of occurrences anchor-entity pairs"""
    sf_dict = {}
    in_file = open(anchor_file)
    i = 0
    for line in in_file:
        i += 1
        cols = line.strip().split("\t")
        if (len(cols) < 4) or (cols[2].strip().lower() == ""):
            continue
        sf = cols[2].strip().lower()
        en = cols[3].strip()
        if sf not in sf_dict:
            sf_dict[sf] = {}
        if en not in sf_dict[sf]:
            sf_dict[sf][en] = 1
        else:
            sf_dict[sf][en] += 1
        if i % 1000000 == 0:
            print i, "th line processed!"

    out_str = ""
    for sf, en_counts in sf_dict.iteritems():
        for en, count in en_counts.iteritems():
            out_str += sf + "\t" + en + "\t" + str(count) + "\n"
    out = open(out_file, "w")
    out.write(out_str)
    out.close()


def main():
    # Builds anchor file
    annotations_dir = "/data/wikipedia/annotations-20120502"
    anchors_file = "/data/wikipedia/preprocessed-20120502/anchors.txt"
    merge_anchors(annotations_dir, anchors_file)
    anchors_count_file = "/data/wikipedia/preprocessed-20120502/anchors_count.txt"
    count_anchors(anchors_file, anchors_count_file)

    # Merges titles, redirects, and anchors
    title_file = "/data/wikipedia/preprocessed-20120502/page-id-titles.txt"
    redirects_file = "/data/wikipedia/preprocessed-20120502/redirects.txt"
    out_file = "/data/wikipedia/preprocessed-20120502/sf_dict_mongo.json"
    merger = Merger()
    merger.merge_all(title_file, redirects_file, anchors_count_file, out_file)

if __name__ == "__main__":
    main()