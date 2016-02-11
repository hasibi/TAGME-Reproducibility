"""
Extracts page id and titles from Wikipedia dump and writes them into a single file

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import argparse
import os
import re


tagRE = re.compile(r'(.*?)(<(/?\w+)[^>]*>)(?:([^<]*)(<.*?>)?)?')
idRE = re.compile(r'id="([0-9]+)"')
titleRE = re.compile(r'title="(.*)"')


def read_file(file_name):
    """Extracts page ids and titles from a single file."""
    out_str = ""
    f = open(file_name, "r")

    for line in f:
        for m in tagRE.finditer(line):
            if not m:
                continue
            tag = m.group(3)
            if tag == "doc":
                doc_id = idRE.search(m.group(2))
                doc_title = titleRE.search(m.group(2))
                if (not doc_id) or (not doc_title):
                    print "\nINFO: doc id or title not found in " + file_name,
                    continue
                out_str += doc_id.group(1) + "\t" + doc_title.group(1) + "\n"
                break
    return out_str


def read_files(basedir, output_file):
    """Extracts page id and titles to a single file."""
    open(output_file, "w").close()
    out_file = open(output_file, "a")
    for path, dirs, _ in os.walk(basedir):
        for dir in sorted(dirs):
            for _, _, files in os.walk(os.path.join(basedir, dir)):
                for fn in sorted(files):
                    print "parsing ", os.path.join(basedir + dir, fn),  "..."
                    out_str = read_file(os.path.join(basedir + dir, fn))
                    out_file.write(out_str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-inputdir", help="Path to directory to read from")
    parser.add_argument("-output", help="Path to write the annotations (.tsv files)")
    args = parser.parse_args()

    read_files(args.inputdir, args.output)
    print "All page ids are added"


if __name__ == "__main__":
    main()
