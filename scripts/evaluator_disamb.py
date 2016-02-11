"""
This script computes evaluation metrics for disambiguation phase.
Foe each query, if the ground truth entity is found in the results, both Precision and recall are set to 1;
otherwise to 0.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

from __future__ import division
import sys
from collections import defaultdict


class EvaluatorDisamb(object):

    def __init__(self, qrels, results, null_qrels=None):
        self.qrels_dict = self.__group_by_queries(qrels)
        self.results_dict = self.__group_by_queries(results)
        self.null_qrels = self.__group_by_queries(null_qrels) if null_qrels else None

    @staticmethod
    def __group_by_queries(file_lines):
        """
        Groups the lines by query id.

        :param file_lines: list of lines [[qid, score, wiki_uri, mention, page_id], ...]
        :return: {qid: {(men0, en0), (men1, en01), ..}, ..};
        """
        grouped_inters = defaultdict(set)
        for cols in file_lines:
            if len(cols) > 2:
                grouped_inters[cols[0]].add((cols[3].lower(), cols[2]))
        return grouped_inters

    def eval(self, eval_query_func):
        """
        Evaluates all queries and calculates total precision, recall and F1 (macro averaging).

        :param eval_query_func: A function that takes qrel and results for a query and returns evaluation metrics
        :return  Total precision, recall, and F1 for all queries
        """
        queries_eval = {}
        total_prec, total_rec, total_f = 0, 0, 0
        for qid in set(sorted(self.qrels_dict)):
            queries_eval[qid] = eval_query_func(self.qrels_dict[qid], self.results_dict.get(qid, {}))
            total_prec += queries_eval[qid]['prec']
            total_rec += queries_eval[qid]['rec']

        n = len(self.qrels_dict)  # number of queries
        total_prec /= n
        total_rec /= n
        total_f = (2 * total_prec * total_rec) / (total_prec + total_rec)

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
    prec, rec = 0, 0

    # ----- Query has at least an interpretation set. -----
    # Iterate over qrels to calculate TP and FN
    for qrel_item in query_qrels:
        if find_item(qrel_item, query_results):
            prec += 1
            rec += 1

    prec /= len(query_qrels)
    rec /= len(query_qrels)
    f = (2 * prec * rec) / (prec + rec) if prec + rec != 0 else 0
    metrics = {'prec': prec, 'rec': rec, 'f': f}
    return metrics


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
        if item[1] == item_to_find[1]:
            is_found = True
    return is_found


def parse_file(file_name, res=False):
    """
    Parses file and returns the positive instances for each query.

    :param file_name: Name of file to be parsed
    :return list of lines [[qid, label, en_id, ...], ...]
    """
    null_lines = []
    file_lines = []
    efile = open(file_name, "r")
    for line in efile.readlines():
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
    results = parse_file(args[1], res=True)[0]
    print "evaluating ..."
    evaluator = EvaluatorDisamb(qrels, results, null_qrels=null_qrels)
    evaluator.eval(erd_eval_query)


if __name__ == '__main__':
    main(sys.argv[1:])
