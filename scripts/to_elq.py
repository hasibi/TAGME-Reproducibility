"""
Converts the results to ELQ format:
 - Filters general concept entities (keeps only proper noun entities)
 - Creates ELQ format file

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import sys
from collections import defaultdict
from nordlys.config import DATA_DIR
from nordlys.wikipedia.utils import WikipediaUtils


def load_kb():
    """Loads Freebase snapshot of proper noun entities."""
    print "Loading knowledge base snapshot ..."
    __fb_dbp_file = open(DATA_DIR + "/fb_dbp_snapshot.txt", "r")
    global KB_SNP_DBP
    for line in __fb_dbp_file:
        cols = line.strip().split("\t")
        KB_SNP_DBP.add(cols[1])
    __fb_dbp_file.close()

KB_SNP_DBP = set()


def read_file(input_file, score_th):
    lines = []
    with open(input_file, "r") as input:
        for line in input:
            cols = line.strip().split("\t")
            if float(cols[1]) < score_th:
                continue
            lines.append(cols)
    return lines


def filter_general_ens(lines):
    """Returns tab-separated lines: qid score   en  men fb_id"""
    filtered_annots = []
    for line in lines:
        dbp_uri = WikipediaUtils.wiki_uri_to_dbp_uri(line[2])
        if dbp_uri in KB_SNP_DBP:  # check fb is in the KB snapshot
            filtered_annots.append(line)
    return filtered_annots


def to_inter_sets(lines):
    """Groups linked entities and interpretation set."""
    group_by_qid = defaultdict(set)
    for cols in lines:
        group_by_qid[cols[0]].add(cols[2])
    return group_by_qid


def main(args):
    if len(args) < 2:
        print "USAGE: <input file> <score threshold>"
        exit(0)
    load_kb()
    lines = read_file(args[0], float(args[1]))
    filtered_annots = filter_general_ens(lines)
    inter_sets = to_inter_sets(filtered_annots)

    out_str = ""
    for qid in sorted(inter_sets.keys()):
        ens = inter_sets[qid]
        out_str += qid + "\t1\t" + "\t".join(ens) + "\n"
    out_file = args[0][:args[0].rfind(".")] + "_" + str(args[1]) + ".elq"
    open(out_file, "w").write(out_str)
    print "Output file:",  out_file


if __name__ == "__main__":
    main(sys.argv[1:])