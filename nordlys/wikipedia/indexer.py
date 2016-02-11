"""
Creates a Lucene index for Wikipedia articles.

- A single field index is created.
- disambiguation and list pages are ignored.
- wiki page annotations are ignored and only mentions are kept.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""
import argparse
import os
import re
from urllib import unquote
from nordlys.wikipedia.utils import WikipediaUtils
from nordlys.tagme.lucene_tools import Lucene


class Indexer(object):
    tagRE = re.compile(r'(.*?)(<(/?\w+)[^>]*>)(?:([^<]*)(<.*?>)?)?')
    idRE = re.compile(r'id="([0-9]+)"')
    titleRE = re.compile(r'title="(.*)"')
    linkRE = re.compile(r'href="(.*)"')

    def __init__(self, annot_only):
        self.annot_only = annot_only
        self.contents = None
        self.lucene = None

    def __add_to_contents(self, field_name, field_value, field_type):
        """
        Adds field to document contents.
        Field value can be a list, where each item is added separately (i.e., the field is multi-valued).
        """
        if type(field_value) is list:
            for fv in field_value:
                self.__add_to_contents(field_name, fv, field_type)
        else:
            if len(field_value) > 0:  # ignore empty fields
                self.contents.append({'field_name': field_name,
                                      'field_value': field_value,
                                      'field_type': field_type})

    def index_file(self, file_name):
        """
        Adds one file to the index.

        :param file_name: file to be indexed
        """
        self.contents = []
        article_text = ""
        article_annots = []  # for annot-only index

        f = open(file_name, "r")
        for line in f:
            line = line.replace("#redirect", "")
            # ------ Reaches the end tag for an article ---------
            if re.search(r'</doc>', line):
                # ignores null titles
                if wiki_uri is None:
                    print "\tINFO: Null Wikipedia title!"
                # ignores disambiguation pages
                elif (wiki_uri.endswith("(disambiguation)>")) or \
                        ((len(article_text) < 200) and ("may refer to:" in article_text)):
                    print "\tINFO: disambiguation page " + wiki_uri + " ignored!"
                # ignores list pages
                elif (wiki_uri.startswith("<wikipedia:List_of")) or (wiki_uri.startswith("<wikipedia:Table_of")):
                    print "\tINFO: List page " + wiki_uri + " ignored!"
                # adds the document to the index
                else:
                    self.__add_to_contents(Lucene.FIELDNAME_ID, wiki_uri, Lucene.FIELDTYPE_ID)
                    if self.annot_only:
                        self.__add_to_contents(Lucene.FIELDNAME_CONTENTS, article_annots, Lucene.FIELDTYPE_ID_TV)
                    else:
                        self.__add_to_contents(Lucene.FIELDNAME_CONTENTS, article_text, Lucene.FIELDTYPE_TEXT_TVP)
                    self.lucene.add_document(self.contents)
                self.contents = []
                article_text = ""
                article_annots = []

            # ------ Process other lines of article ---------
            tag_iter = list(self.tagRE.finditer(line))
            # adds line to content if there is no annotation
            if len(tag_iter) == 0:
                article_text += line
                continue
            # A tag is detected in the line
            for t in tag_iter:
                tag = t.group(3)
                if tag == "doc":
                    doc_title = self.titleRE.search(t.group(2))
                    wiki_uri = WikipediaUtils.wiki_title_to_uri(doc_title.group(1)) if doc_title else None
                if tag == "a":
                    article_text += t.group(1) + t.group(4)  # resolves annotations and replace them with mention
                    # extracts only annotations
                    if self.annot_only:
                        link_title = self.linkRE.search(t.group(2))
                        link_uri = WikipediaUtils.wiki_title_to_uri(unquote(link_title.group(1))) if link_title else None
                        if link_uri is not None:
                            article_annots.append(link_uri)
                        else:
                            print "\nINFO: link to the annotation not found in " + file_name
            last_span = tag_iter[-1].span()
            article_text += line[last_span[1]:]
        f.close()

    def index_files(self, input_dir, output_dir):
        """Build index for all files."""
        self.lucene = Lucene(output_dir)
        self.lucene.open_writer()
        for path, dirs, _ in os.walk(input_dir):
            for dir in sorted(dirs):
                for _, _, files in os.walk(os.path.join(input_dir, dir)):
                    for fn in sorted(files):
                        print "Indexing ", os.path.join(input_dir + dir, fn),  "..."
                        self.index_file(os.path.join(input_dir + dir, fn))
        # closes Lucene index
        self.lucene.close_writer()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-inputdir", help="Path to directory to read from")
    parser.add_argument("-outputdir", help="Path to write the annotations (.tsv files)")
    parser.add_argument("-annot", help="Annotation-only index", action="store_true", default=False)

    args = parser.parse_args()

    output_dir = args.outputdir
    input_dir = args.inputdir
    print "index dir: " + output_dir
    indexer = Indexer(args.annot)
    indexer.index_files(input_dir, output_dir)
    print "index build" + output_dir


if __name__ == "__main__":
    main()