"""
Filters tagme results
"""
from collections import defaultdict
import sys
from nordlys.tagme.econfig import DATA_DIR, ENTITY


def load_kb():
    # Freebase and Wiki ids of proper noun entities.
    print "Loading knowledge base snapshot ..."
    FB_DBP_FILE = DATA_DIR + "/fb_dbp_snapshot.txt"
    __fb_dbp_file = open(FB_DBP_FILE, "r")
    global KB_SNP_DBP, KB_SNP_FB
    for line in __fb_dbp_file:
        cols = line.strip().split("\t")
        KB_SNP_DBP.add(cols[1])
        # KB_SNP_FB.add(cols[0])
    __fb_dbp_file.close()

KB_SNP_DBP = set()
# KB_SNP_FB = set()


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
    """Returns tab-seperated lines: qid score   en  men fb_id"""
    filtered_annots = []
    for line in lines:
        dbp_uri = ENTITY.wiki_uri_to_dbp_uri(line[2])
        if dbp_uri in KB_SNP_DBP:  # check fb is in the KB snapshot
            filtered_annots.append(line)
    return filtered_annots

def to_inter_sets(lines):
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
    out_file = args[0][:args[0].rfind(".")] + "_" + str(args[1]) +".erdeval"
    open(out_file, "w").write(out_str)
    print "Output file:",  out_file


if __name__ == "__main__":
    main(sys.argv[1:])