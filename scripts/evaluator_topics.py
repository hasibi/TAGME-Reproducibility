"""
This script computes Topic metrics for the end-to-end performance.
Precision and recall are micro-averaged.
Matching condition: only entities should match.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

from __future__ import division
import sys
from collections import defaultdict


class EvaluatorTopics(object):

    def __init__(self, qrels, results, null_qrels=None, score_th=0):
        self.qrels_dict = self.__group_by_queries(qrels)
        self.results_dict = self.__group_by_queries(results, score_th=score_th)
        self.null_qrels = self.__group_by_queries(null_qrels) if null_qrels else None
        self.score_th = score_th

    @staticmethod
    def __group_by_queries(file_lines, score_th=None):
        """
        Groups the lines by query id.

        :param file_lines: list of lines [[qid, score, en_id, mention, page_id], ...]
        :return: {qid: {(men0, en0), (men1, en01), ..}, ..};
        """
        grouped_inters = defaultdict(set)
        for cols in file_lines:
            if len(cols) > 2:
                if score_th and (float(cols[1]) < score_th):
                    continue
                grouped_inters[cols[0]].add((cols[3].lower(), cols[2].lower()))
        return grouped_inters

    def rm_nulls_res(self):
        """
        Removes mentions that not linked to an entity in the qrel.
        There are some entities in the qrel with "*NONE*" as id. We remove the related mentions from the result file.
        Null entities are generated due to the inconsistency between TAGME Wikipedia dump (2009) and our dump (2010).
        """
        print "Removing mentions with null entities ..."
        new_results_dict = defaultdict(set)
        for qid in self.results_dict:
            # easy case
            if qid not in set(self.null_qrels.keys()):
                new_results_dict[qid] = self.results_dict[qid]
                continue

            qrel_null_mentions = [item[0] for item in self.null_qrels[qid]]
            # check null mentions with results mentions
            for men, en in self.results_dict[qid]:
                is_null = False
                for qrel_null_men in qrel_null_mentions:
                    # results mention does not match null qrel mention
                    if mention_match(qrel_null_men, men):
                        is_null = True
                        break

                if not is_null:
                    new_results_dict[qid].add((men, en))
                # else:
                    # print qid, men, en, "QREL mention:", qrel_null_men, "-*-"
        self.results_dict = new_results_dict

    def eval(self, eval_query_func):
        """
        Evaluates all queries and calculates total precision, recall and F1 (macro averaging).

        :param eval_query_func: A function that takes qrel and results for a query and returns evaluation metrics
        :return  Total precision, recall, and F1 for all queries
        """
        self.rm_nulls_res()
        print "comparing results ..."
        queries_eval = {}
        total_tp, total_fp, total_fn = 0, 0, 0
        for qid in sorted(self.qrels_dict):
            queries_eval[qid] = eval_query_func(self.qrels_dict[qid], self.results_dict.get(qid, {}))

            total_tp += queries_eval[qid]['tp']
            total_fp += queries_eval[qid]['fp']
            total_fn += queries_eval[qid]['fn']

        total_prec = total_tp / (total_tp + total_fp)
        total_rec = total_tp / (total_tp + total_fn)
        total_f = 2 * total_prec * total_rec / (total_prec + total_rec)

        log = "\n----------------" + "\nEvaluation results:\n" + \
              "Prec: " + str(round(total_prec, 4)) + "\n" +\
              "Rec:  " + str(round(total_rec, 4)) + "\n" + \
              "F1:   " + str(round(total_f, 4)) + "\n" + \
              "all:  " + str(round(total_prec, 4)) + ", " + str(round(total_rec, 4)) + ", " + str(round(total_f, 4))
        print log
        metrics = {'prec': total_prec, 'rec': total_rec, 'f': total_f}
        return metrics


def erd_eval_query(query_qrels, query_results):
    """
    Evaluates a single query.

    :param query_qrels: Query interpretations from Qrel [{en1, en2, ..}, ..]
    :param query_results: Query interpretations from result file [{en1, en2, ..}, ..]
    :return: precision, recall, and F1 for a query
    """
    tp = 0  # correct
    fn = 0  # missed
    fp = 0  # incorrectly returned

    # ----- Query has at least an interpretation set. -----
    # Iterate over qrels to calculate TP and FN
    results_ens = [item[1] for item in query_results]
    qrel_ens = [item[1] for item in query_qrels]
    for qrel_item in qrel_ens:
        if find_item(qrel_item, results_ens):
            tp += 1
        else:
            fn += 1
    # Iterate over results to calculate FP
    for res_item in results_ens:
        if not find_item(res_item, qrel_ens):  # Finds the result in the qrels
            fp += 1

    stats = {'tp': tp, 'fp': fp, 'fn': fn}
    return stats


def find_item(item_to_find, items_list):
    """
    Returns True if an item is found in the item list.

    :param item_to_find: item to be found
    :param items_list: list of items to search in
    :return boolean
    """
    is_found = False
    item_to_find = item_to_find
    for item in items_list:
        if item == item_to_find:
            is_found = True
    return is_found


def mention_match(mention1, mention2):
    """
    Checks if two mentions matches each other.
    Matching condition: One of the mentions is sub-string of the other one.
    """
    match = ((mention1 in mention2) or (mention2 in mention1))
    return match


def parse_file(file_name, res=False):
    """
    Parses file and returns the positive instances for each query.

    :param file_name: Name of file to be parsed
    :return list of lines [[qid, score, en_id, mention, ...], ...]
    """
    null_lines = []
    file_lines = []
    infile = open(file_name, "r")
    for line in infile.readlines():
        if line.strip() == "":
            continue
        cols = line.strip().split("\t")
        if (not res) and (cols[2].strip() == "*NONE*"):
            null_lines.append(cols)
        else:
            file_lines.append(cols)
    return file_lines, null_lines


def main(args):
    if len(args) < 2:
        print "\tUsage: <qrel_file> <result_file>"
        exit(0)
    print "parsing qrel ..."
    qrels, null_qrels = parse_file(args[0])  # here qrel does not contain null entities
    print "parsing results ..."
    results = parse_file(args[1])[0]
    print "evaluating ..."
    score_th = 0 if len(args) == 2 else float(args[2])
    evaluator = EvaluatorTopics(qrels, results, null_qrels=null_qrels, score_th=score_th)
    evaluator.eval(erd_eval_query)

if __name__ == '__main__':
    main(sys.argv[1:])
