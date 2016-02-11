"""
Tools for processing queries.
This class finds all n_grams and the candidate entities for a query.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import re


class Query(object):
    def __init__(self, qid, query):
        self.id = qid
        self.query = self.preprocess(query).lower()

    @staticmethod
    def preprocess(input_str):
        """Pre-process the query; removes some special chars."""
        input_str = re.sub('[^A-Za-z0-9]+', ' ', input_str)
        input_str = input_str.replace(" OR ", " ").replace(" AND ", " ")
        # removing multiple spaces
        cleaned_str = ' '.join(input_str.split())
        return cleaned_str

    def get_ngrams(self):
        """
        Finds all n-grams of the query.

        :return list of n-grams
        """
        con = self.query.strip().split()
        ngrams = []
        for i in range(1, len(con) + 1):  # number of words
            for start in range(0, len(con) - i + 1):  # start point
                ngram = con[start]
                for j in range(1, i):  # builds the sub-string
                    ngram += " " + con[start + j]
                ngrams.append(ngram)
        return ngrams
