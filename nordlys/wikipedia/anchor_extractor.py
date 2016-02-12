"""
Creates a single anchor file for all entity-linking annotations.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""
import argparse
import os


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
    parser = argparse.ArgumentParser()
    parser.add_argument("-inputdir", help="Path to directory to read from")
    parser.add_argument("-outputdir", help="Path to write the annotations (.tsv files)")
    args = parser.parse_args()

    merge_anchors(args.inputdir, args.outputdir + "/anchors.txt")
    count_anchors(args.outputdir + "/anchors.txt", args.outputdir + "/anchors_count.txt")

if __name__ == "__name__":
    main()