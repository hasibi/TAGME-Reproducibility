"""
Extracts annotations from processed Wikipedia articles and writes them in .tsv files.

author: Faegheh Hasibi
"""

import argparse
import os
import re
from datetime import datetime

tagRE = re.compile(r'(.*?)(<(/?\w+)[^>]*>)(?:([^<]*)(<.*?>)?)?')
idRE = re.compile(r'id="([0-9]+)"')
titleRE = re.compile(r'title="(.*)"')
linkRE = re.compile(r'href="(.*)"')


def process_file(wiki_file, out_file):
    """
    Extracts annotations from XML annotated file and write annotations.
    output file format: page_id   title   mention    linked_en

    :param wiki_file:  XML file containing multiple articles.
    :param out_file: Name of tsv file.
    """
    print "Processing " + wiki_file + " ...",
    open(out_file, "w").close()
    out = open(out_file, "a")
    f = open(wiki_file, "r")
    annots = []
    doc_id, doc_title = None, None
    for line in f:
        # Writes annotations and reset variables
        if re.search(r'</doc>', line):
            out.write("".join(annots))
            annots = []
            doc_id, doc_title = None, None
        for m in tagRE.finditer(line):
            if not m:
                continue
            tag = m.group(3)
            if tag == "doc":
                doc_id = idRE.search(m.group(2))
                doc_title = titleRE.search(m.group(2))
                if (not doc_id) or (not doc_title):
                    print "\nINFO: doc id or title not found in " + wiki_file,
                    continue
            if tag == "a":
                mention = m.group(4)
                link = linkRE.search(m.group(2))
                if (not link) or (doc_id is None) or (doc_title is None):
                    print "\nINFO: link not found in " + wiki_file,
                    continue
                annot = doc_id.group(1) + "\t" + doc_title.group(1) + "\t" + mention + "\t" + link.group(1) + "\n"
                annots.append(annot)
    print " --> output in " + out_file


def add_dir(base_in_dir, base_out_dir):
    """Adds FACC annotations from a directory recursively."""
    for path, dirs, _ in os.walk(base_in_dir):
        for dir in sorted(dirs):
            s_t = datetime.now()  # start time
            total_time = 0.0
            for _, _, files in os.walk(os.path.join(base_in_dir, dir)):
                for fn in files:
                    out_dir = base_out_dir + dir
                    if not os.path.exists(out_dir):
                        os.makedirs(out_dir)
                    out_file = os.path.join(out_dir,  "an_" + fn + ".tsv")
                    in_file = os.path.join(base_in_dir + dir, fn)
                    process_file(in_file, out_file)

            e_t = datetime.now()  # end time
            diff = e_t - s_t
            total_time += diff.total_seconds()
            print "[processing time for bunch " + dir + " (min)]:", total_time/60


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-inputdir", help="Path to directory to read from")
    parser.add_argument("-outputdir", help="Path to write the annotations (.tsv files)")
    args = parser.parse_args()

    add_dir(args.inputdir, args.outputdir)

if __name__ == "__main__":
    main()
