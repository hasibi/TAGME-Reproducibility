"""
TAGME implementation

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import argparse
import math
from nordlys.config import OUTPUT_DIR
from nordlys.tagme import config
from nordlys.tagme import test_coll
from nordlys.tagme.query import Query
from nordlys.tagme.mention import Mention
from nordlys.tagme.lucene_tools import Lucene


ENTITY_INDEX = Lucene(config.INDEX_PATH)
ANNOT_INDEX = Lucene(config.INDEX_ANNOT_PATH, use_ram=True)

# ENTITY_INDEX = IndexCache("/data/wikipedia-indices/20120502-index1")
# ANNOT_INDEX = IndexCache("/data/wikipedia-indices/20120502-index1-annot/", use_ram=True)

ENTITY_INDEX.open_searcher()
ANNOT_INDEX.open_searcher()


class Tagme(object):

    DEBUG = 0

    def __init__(self, query, rho_th, sf_source="wiki"):
        self.query = query
        self.rho_th = rho_th
        self.sf_source = sf_source

        # TAMGE params
        self.link_prob_th = 0.001
        self.cmn_th = 0.02
        self.k_th = 0.3

        self.link_probs = {}
        self.in_links = {}
        self.rel_scores = {}  # dictionary {men: {en: rel_score, ...}, ...}
        self.disamb_ens = {}

    def parse(self):
        """
        Parses the query and returns all candidate mention-entity pairs.

        :return: candidate entities {men:{en:cmn, ...}, ...}
        """
        ens = {}
        for ngram in self.query.get_ngrams():
            mention = Mention(ngram)
            # performs mention filtering (based on the paper)
            if (len(ngram) == 1) or (ngram.isdigit()) or (mention.wiki_occurrences < 2) or (len(ngram.split()) > 6):
                continue
            link_prob = self.__get_link_prob(mention)
            if link_prob < self.link_prob_th:
                continue
            # These mentions will be kept
            self.link_probs[ngram] = link_prob
            # Filters entities by cmn threshold 0.001; this was only in TAGME source code and speeds up the process.
            # TAGME source code: it.acubelab.tagme.anchor (lines 279-284)
            ens[ngram] = mention.get_men_candidate_ens(0.001)

        # filters containment mentions (based on paper)
        candidate_entities = {}
        sorted_mentions = sorted(ens.keys(), key=lambda item: len(item.split()))  # sorts by mention length
        for i in range(0, len(sorted_mentions)):
            m_i = sorted_mentions[i]
            ignore_m_i = False
            for j in range(i+1, len(sorted_mentions)):
                m_j = sorted_mentions[j]
                if (m_i in m_j) and (self.link_probs[m_i] < self.link_probs[m_j]):
                    ignore_m_i = True
                    break
            if not ignore_m_i:
                candidate_entities[m_i] = ens[m_i]
        return candidate_entities

    def disambiguate(self, candidate_entities):
        """
        Performs disambiguation and link each mention to a single entity.

        :param candidate_entities: {men:{en:cmn, ...}, ...}
        :return: disambiguated entities {men:en, ...}
        """
        # Gets the relevance score
        rel_scores = {}
        for m_i in candidate_entities.keys():
            if self.DEBUG:
                print "********************", m_i, "********************"
            rel_scores[m_i] = {}
            for e_m_i in candidate_entities[m_i].keys():
                if self.DEBUG:
                    print "-- ", e_m_i
                rel_scores[m_i][e_m_i] = 0
                for m_j in candidate_entities.keys():  # all other mentions
                    if (m_i == m_j) or (len(candidate_entities[m_j].keys()) == 0):
                        continue
                    vote_e_m_j = self.__get_vote(e_m_i, candidate_entities[m_j])
                    rel_scores[m_i][e_m_i] += vote_e_m_j
                    if self.DEBUG:
                        print m_j, vote_e_m_j

        # pruning uncommon entities (based on the paper)
        self.rel_scores = {}
        for m_i in rel_scores:
            for e_m_i in rel_scores[m_i]:
                cmn = candidate_entities[m_i][e_m_i]
                if cmn >= self.cmn_th:
                    if m_i not in self.rel_scores:
                        self.rel_scores[m_i] = {}
                    self.rel_scores[m_i][e_m_i] = rel_scores[m_i][e_m_i]

        # DT pruning
        disamb_ens = {}
        for m_i in self.rel_scores:
            if len(self.rel_scores[m_i].keys()) == 0:
                continue
            top_k_ens = self.__get_top_k(m_i)
            best_cmn = 0
            best_en = None
            for en in top_k_ens:
                cmn = candidate_entities[m_i][en]
                if cmn >= best_cmn:
                    best_en = en
                    best_cmn = cmn
            disamb_ens[m_i] = best_en

        return disamb_ens

    def prune(self, dismab_ens):
        """
        Performs AVG pruning.

        :param dismab_ens: {men: en, ... }
        :return: {men: (en, score), ...}
        """
        linked_ens = {}
        for men, en in dismab_ens.iteritems():
            coh_score = self.__get_coherence_score(men, en, dismab_ens)
            rho_score = (self.link_probs[men] + coh_score) / 2.0
            if rho_score >= self.rho_th:
                linked_ens[men] = (en, rho_score)
        return linked_ens

    def __get_link_prob(self, mention):
        """
        Gets link probability for the given mention.
        Here, in fact, we are computing key-phraseness.
        """

        pq = ENTITY_INDEX.get_phrase_query(mention.text, Lucene.FIELDNAME_CONTENTS)
        mention_freq = ENTITY_INDEX.searcher.search(pq, 1).totalHits
        if mention_freq == 0:
            return 0
        if self.sf_source == "wiki":
            link_prob = mention.wiki_occurrences / float(mention_freq)
            # This is TAGME implementation, from source code:
            # link_prob = float(mention.wiki_occurrences) / max(mention_freq, mention.wiki_occurrences)
        elif self.sf_source == "facc":
            link_prob = mention.facc_occurrences / float(mention_freq)
        return link_prob

    def __get_vote(self, entity, men_cand_ens):
        """
        vote_e = sum_e_i(mw_rel(e, e_i) * cmn(e_i)) / i

        :param entity: en
        :param men_cand_ens: {en: cmn, ...}
        :return: voting score
        """
        entity = entity if self.sf_source == "wiki" else entity[0]
        vote = 0
        for e_i, cmn in men_cand_ens.iteritems():
            e_i = e_i if self.sf_source == "wiki" else e_i[0]
            mw_rel = self.__get_mw_rel(entity, e_i)
            # print "\t", e_i, "cmn:", cmn, "mw_rel:", mw_rel
            vote += cmn * mw_rel
        vote /= float(len(men_cand_ens))
        return vote

    def __get_mw_rel(self, e1, e2):
        """
        Calculates Milne & Witten relatedness for two entities.
        This implementation is based on Dexter implementation (which is similar to TAGME implementation).
          - Dexter implementation: https://github.com/dexter/dexter/blob/master/dexter-core/src/main/java/it/cnr/isti/hpc/dexter/relatedness/MilneRelatedness.java
          - TAGME: it.acubelab.tagme.preprocessing.graphs.OnTheFlyArrayMeasure
        """
        if e1 == e2:  # to speed-up
            return 1.0
        en_uris = tuple(sorted({e1, e2}))
        ens_in_links = [self.__get_in_links([en_uri]) for en_uri in en_uris]
        if min(ens_in_links) == 0:
            return 0
        conj = self.__get_in_links(en_uris)
        if conj == 0:
            return 0
        numerator = math.log(max(ens_in_links)) - math.log(conj)
        denominator = math.log(ANNOT_INDEX.num_docs()) - math.log(min(ens_in_links))
        rel = 1 - (numerator / denominator)
        if rel < 0:
            return 0
        return rel

    def __get_in_links(self, en_uris):
        """
        returns "and" occurrences of entities in the corpus.

        :param en_uris: list of dbp_uris
        """
        en_uris = tuple(sorted(set(en_uris)))
        if en_uris in self.in_links:
            return self.in_links[en_uris]

        term_queries = []
        for en_uri in en_uris:
            term_queries.append(ANNOT_INDEX.get_id_lookup_query(en_uri, Lucene.FIELDNAME_CONTENTS))
        and_query = ANNOT_INDEX.get_and_query(term_queries)
        self.in_links[en_uris] = ANNOT_INDEX.searcher.search(and_query, 1).totalHits
        return self.in_links[en_uris]

    def __get_coherence_score(self, men, en, dismab_ens):
        """
        coherence_score = sum_e_i(rel(e_i, en)) / len(ens) - 1

        :param en: entity
        :param dismab_ens: {men:  (dbp_uri, fb_id), ....}
        """
        coh_score = 0
        for m_i, e_i in dismab_ens.iteritems():
            if m_i == men:
                continue
            coh_score += self.__get_mw_rel(e_i, en)
        coh_score = coh_score / float(len(dismab_ens.keys()) - 1) if len(dismab_ens.keys()) - 1 != 0 else 0
        return coh_score

    def __get_top_k(self, mention):
        """Returns top-k percent of the entities based on rel score."""
        k = int(round(len(self.rel_scores[mention].keys()) * self.k_th))
        k = 1 if k == 0 else k
        sorted_rel_scores = sorted(self.rel_scores[mention].items(), key=lambda item: item[1], reverse=True)
        top_k_ens = []
        count = 1
        prev_rel_score = sorted_rel_scores[0][1]
        for en, rel_score in sorted_rel_scores:
            if rel_score != prev_rel_score:
                count += 1
            if count > k:
                break
            top_k_ens.append(en)
            prev_rel_score = rel_score
        return top_k_ens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-th", "--threshold", help="score threshold", type=float, default=0)
    parser.add_argument("-data", help="Data set name", choices=['y-erd', 'erd-dev', 'wiki-annot30', 'wiki-disamb30'])
    args = parser.parse_args()

    if args.data == "erd-dev":
        queries = test_coll.read_erd_queries()
    elif args.data == "y-erd":
        queries = test_coll.read_yerd_queries()
    elif args.data == "wiki-annot30":
        queries = test_coll.read_tagme_queries(config.WIKI_ANNOT30_SNIPPET)
    elif args.data == "wiki-disamb30":
        queries = test_coll.read_tagme_queries(config.WIKI_DISAMB30_SNIPPET)

    out_file_name = OUTPUT_DIR + "/" + args.data + "_tagme_wiki10.txt"
    open(out_file_name, "w").close()
    out_file = open(out_file_name, "a")

    # process the queries
    for qid, query in sorted(queries.items(), key=lambda item: int(item[0]) if item[0].isdigit() else item[0]):
        print "[" + qid + "]", query
        tagme = Tagme(Query(qid, query), args.threshold)
        print "  parsing ..."
        cand_ens = tagme.parse()
        print "  disambiguation ..."
        disamb_ens = tagme.disambiguate(cand_ens)
        print "  pruning ..."
        linked_ens = tagme.prune(disamb_ens)

        out_str = ""
        for men, (en, score) in linked_ens.iteritems():
            out_str += str(qid) + "\t" + str(score) + "\t" + en + "\t" + men + "\tpage-id" + "\n"
        print out_str, "-----------\n"
        out_file.write(out_str)

    print "output:", out_file_name


if __name__ == "__main__":
    main()