"""
Tools for processing queries.
This class finds all n_grams and the candidate entities for a query.

@author: Faegheh Hasibi
"""

import sys
import re
from nordlys.entity.freebase.utils import FreebaseUtils

from nordlys.tagme import econfig


class Query(object):
    """
    Methods for processing a query.
    - NOTE: Each query is pre-processed using rm_stop_chars() function.

    Attributes:
        id: string
        content: string

    """
    def __init__(self, qid, content):
        self.id = qid
        self.content = self.preprocess(content).lower()

    @staticmethod
    def preprocess(input_str):
        """Pre-process the query; removes some special chars."""
        # replace special chars with space
        # s_list = "\"':,;.&!?+()[]\\/"
        # for ch in s_list:
        #     input_str = input_str.replace(ch, " ")
        input_str = re.sub('[^A-Za-z0-9]+', ' ', input_str)
        input_str = input_str.replace(" OR ", " ").replace(" AND ", " ")
        # removing multiple spaces
        cleaned_str = ' '.join(input_str.split())
        return cleaned_str

    @staticmethod
    def remove_stop_words(input_str, stop_words=None):
        """
        Removes stop words from query.
        Stop words extracted from Lucene standardAnalyzer.STOP_WORDS_SET
        """
        # NOTE: This method not used for our experiments
        # stop_words = {"but", "be", "with", "such", "then", "for", "no", "will", "not", "are", "and", "their", "if",
        #               "this", "on", "into", "a", "or", "there", "in", "that", "they", "was", "is", "it", "an", "the",
        #               "as", "at", "these", "by", "to", "of"}
        new_str = ""
        for term in input_str.strip().split():
            if term not in stop_words:
                new_str += term + " "
        return new_str.strip()

    def get_terms(self, lucene=None):
        """
        Gets query terms.
        if lucene object is passed, lucene query analyzer is used.
        Otherwise, terms are obtained by splitting the query terms by space.

        :return: list of query terms
        """
        if lucene is not None:
            query_terms = lucene.analyze_query(self.content)
        else:
            query_terms = self.content.split()
        return query_terms

    def get_ngrams(self):
        """
        Finds all n-grams of the query.

        :return list of n-grams
        """
        con = self.content.strip().split()
        ngrams = []
        for i in range(1, len(con) + 1):  # number of words
            for start in range(0, len(con) - i + 1):  # start point
                ngram = con[start]
                for j in range(1, i):  # builds the sub-string
                    ngram += " " + con[start + j]
                ngrams.append(ngram)
        return ngrams

    def get_candidate_entities(self, commonness_th, sf_source=None, filter=True):
        """
        Finds all candidate entities for the given query.
            - generates all n_grams
            - Detect all entities whose surface form matches query n-grams.

        :param commonness_th: float, commonness threshold
        :param sf_source: one of the values [facc | wiki]
        :param filter: Filter proper-named entities or not
        :return A dictionary, where each entry has a list of entityIds: {ngram:[(dbp_uri, fb_id):commonness, ..], ..}
        """
        candidate_entities = {}
        for ngram in self.get_ngrams():
            mention = Mention(ngram, sf_source)
            unfiltered_ens = mention.get_men_candidate_ens(commonness_th, filter=False)
            if filter:
                filtered_ens = mention.filter_cand_ens(unfiltered_ens)
                candidate_entities[ngram] = (filtered_ens, len(unfiltered_ens))
            else:
                candidate_entities[ngram] = (unfiltered_ens, len(unfiltered_ens))
        return candidate_entities

    def candidate_entities_to_str(self, candidate_entities):
        """
        Converts candidate entities to the string.
        Returns:
            A tab separated string in the following format:
                "content    ngram    enId1    enId2    ..."
        """
        out = ""
        for srf in candidate_entities:
            out += self.content + "\t" + srf + "\t"
            for en_id, commonness in candidate_entities[srf][0].iteritems():
                out += "{" + str(en_id) + ", " + str(commonness) + "}\t"
            out += "\n"
        return out


class Mention(object):
    """
    Attribute:
        text: substring of query
        sf_source: set, surface form sources from ["facc" | "wiki"]

    """
    ENTITY = econfig.ENTITY
    SF = econfig.SF
    SF_WIKI = econfig.SF_WIKI10
    # SF_WIKI = econfig.SF_WIKI12

    def __init__(self, text, sf_source):
        self.text = text.lower()
        self.sf_source = sf_source
        self.__matched_ens = None       # all entities matching a mention (from all sources)
        self.__merged_facc = None       # merged facc'09 and facc'12
        self.__facc_occurrences = None  # used as denominator of commonness
        self.__wiki_occurrences = None

    @property
    def matched_ens(self):
        return self.__gen_matched_ens()

    @property
    def merged_facc(self):
        return self.__gen_merged_facc()

    @property
    def facc_occurrences(self):
        self.__gen_merged_facc()
        return self.__facc_occurrences

    @property
    def wiki_occurrences(self):
        return self.__calc_wiki_occurences()

    def __gen_matched_ens(self):
        """Gets all entities matching the n-gram {'facc09':{...}, 'facc12':{...}, ...}"""
        if self.__matched_ens is None:
            matches = {}
            if "facc" == self.sf_source:
                matches = Mention.SF.get(self.text)
            if "wiki" == self.sf_source:
                matches = Mention.SF_WIKI.get(self.text)
            matched_ens = matches if matches is not None else {}
            self.__matched_ens = matched_ens
        return self.__matched_ens

    def __gen_merged_facc(self):
        """
        Merges freebase annotations of the two clueweb corpora and
          adds-up occurrences of an entity if it appears on both datasets.

        Note: We merged these two steps into one, because of efficiency!
        """
        if self.__merged_facc is None:
            facc09 = self.matched_ens.get('facc09', {})
            facc12 = self.matched_ens.get('facc12', {})
            merged_facc = facc09
            self.__facc_occurrences = sum(facc09.values())
            for fb_uri, occurrences in facc12.iteritems():
                if fb_uri in merged_facc:
                    merged_facc[fb_uri] += occurrences
                else:
                    merged_facc[fb_uri] = occurrences
                self.__facc_occurrences += occurrences
            self.__merged_facc = merged_facc
        return self.__merged_facc

    def __calc_wiki_occurences(self):
        """Calculates the denominator for commonness (for Wiki annotations)."""
        if self.__wiki_occurrences is None:
            self.__wiki_occurrences = 0
            for en, occ in self.matched_ens.get('anchor', {}).iteritems():
                self.__wiki_occurrences += occ
        return self.__wiki_occurrences

    def get_men_candidate_ens(self, commonness_th, filter=True):
        """
        Gets candidate entities for the given n-gram.

        :param commonness_th: commonness threshold
        :param filter: if True, filters entities that are not in the KB snapshot
        :return: dictionary {(dbp_uri, fb_id):commonness, ..}
        """
        candidate_entities = {}
        # gets facc matches (with dbpedia uri)
        if "facc" == self.sf_source:
            facc_matches = self.get_facc_matches(commonness_th)
            candidate_entities.update(facc_matches)
            ignore_list = [en_id[0] for en_id in facc_matches.keys()]
            dbp_matches = self.get_dbp_matches(ignore_list)
            candidate_entities.update(dbp_matches)

        # gets wiki matches (with fb id)
        if "wiki" == self.sf_source:
            wiki_matches = self.get_wiki_matches(commonness_th)
            candidate_entities.update(wiki_matches)

        # Performs filtering
        if filter:
            return self.filter_cand_ens(candidate_entities)
        return candidate_entities

    def filter_cand_ens(self, cand_ens):
        """
        Filters entities that are not in KB snapshot.

        :param cand_ens: dictionary {(dbp_uri, fb_id):commonness, ..}
        :return: Filtered candidate entities.
        """
        filtered_ens = {}
        for (dbp_uri, fb_id), cmn in cand_ens.iteritems():
            if fb_id in econfig.KB_SNP_FB:   # if dbp_uri in econfig.KB_SNP_DBP:
                filtered_ens[(dbp_uri, fb_id)] = cmn
        return filtered_ens

    def get_facc_matches(self, commonness_th):
        """
        Gets entity matches from FACC09, FACC12 (with dbpedia uris).

        :param commonness_th: float, Commonness threshold
        :return: Dictionary {(dbp_uri, fb_id): commonness, ...}
        """
        if commonness_th is None:
            commonness_th = 0

        facc_matches = {}
        # calculates commonness for each entity and filter uncommon ones
        for fb_uri in self.merged_facc:
            cmn = self.calc_commonness(fb_uri)
            if cmn >= commonness_th:
                fb_id = FreebaseUtils.freebase_uri_to_id(fb_uri)
                dbp_uri = self.ENTITY.fb_id_to_dbp_uri(fb_id)
                if dbp_uri is not None:
                    facc_matches[(dbp_uri, fb_id)] = cmn
        return facc_matches

    def get_wiki_matches(self, commonness_th):
        """
        Gets entity matches from Wikipedia anchors (with dbpedia uris).

        :param commonness_th: float, Commonness threshold
        :return: Dictionary {(dbp_uri, fb_id): commonness, ...}

        """
        if commonness_th is None:
            commonness_th = 0

        wiki_matches = {}
        # calculates commonness for each entity and filter the ones below the commonness threshold.
        for wiki_uri in self.matched_ens.get("anchor", {}):
            cmn = self.calc_commonness(wiki_uri)
            if cmn >= commonness_th:
                wiki_matches[wiki_uri] = cmn

        sources = ["title", "title-nv", "redirect"]
        for source in sources:
            for wiki_uri in self.matched_ens.get(source, {}):
                if wiki_uri not in wiki_matches:
                    cmn = self.calc_commonness(wiki_uri)
                    wiki_matches[wiki_uri] = cmn
        return wiki_matches

    def get_dbp_matches(self, ignore_list):
        """
        Gets entity matches from DBpedia name variants.

        :param ignore_list: commonness will not be calculated for these entities (they are in common with FACC/wiki)
        :return: Dictionary {(dbpe_uri, fb_id): commonness, ...}
        """
        dbp_uris = []
        for predicate, ens in self.matched_ens.iteritems():
            if (predicate != "facc09") and (predicate != "facc12"):
                dbp_uris += ens.keys()
        # Adds commonness to the dbpedia uris
        dbp_matches = {}
        for dbp_uri in set(dbp_uris):
            if dbp_uri in ignore_list:
                continue
            fb_id = self.ENTITY.dbp_uri_to_fb_id(dbp_uri)
            if fb_id is None:
                continue
            fb_uri = FreebaseUtils.freebase_id_to_uri(fb_id)
            cmn = self.calc_commonness(fb_uri)
            dbp_matches[(dbp_uri, fb_id)] = cmn
        return dbp_matches

    def calc_commonness(self, en_uri):
        """
        Calculates commonness for the given entity:
            (times mention is linked) / (times mention linked to entity)
            - Returns zero if the entity is not linked by the mention.

        :param en_uri: freebase uri
        :return Commonness
        """

        cmn = 0
        if "facc" == self.sf_source:
            if en_uri.startswith("<dbpedia:"):
                en_uri = econfig.ENTITY.dbp_uri_to_fb_uri(en_uri)
            if en_uri in self.merged_facc:
                cmn = self.merged_facc[en_uri] / float(self.facc_occurrences)

        elif "wiki" == self.sf_source:
            if not en_uri.startswith("<wikipedia:"):
                raise Exception("Only Wikipedia URI should be passed to commonness!")
            cmn = self.matched_ens.get('anchor', {}).get(en_uri, 0) / float(self.wiki_occurrences)
        return cmn


def main(argv):
    #    q1 = "tn highway patrol" #"the music man"
    #    q2 = "battles in the civil war"
    #    q30 = "gmat prep classes"
    #    q57 = "pacific northwest laboratory"
    #    q62 = "rincon puerto rico"
    #    q63 = "ritz carlton lake las vegas"
    #    q75 = "the secret garden"
    #    q82 = "uplift at yellowstone national park"
    #    q86 = "va dmv registration"
    query = Query("TREC-1", argv[0])
    can_ens = query.get_candidate_entities(0.1, sf_source="facc", filter=False)
    print "Candidate entities to string ..."
    print query.candidate_entities_to_str(can_ens)

if __name__ == "__main__":
    main(sys.argv[1:])
