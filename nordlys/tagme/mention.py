"""
Tools for processing mentions:
  -  Finds candidate entities
  -  Calculates commonness

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

from nordlys.tagme.config import SF_WIKI


class Mention(object):

    def __init__(self, text):
        self.text = text.lower()
        self.__matched_ens = None       # all entities matching a mention (from all sources)
        self.__wiki_occurrences = None

    @property
    def matched_ens(self):
        return self.__gen_matched_ens()

    @property
    def wiki_occurrences(self):
        return self.__calc_wiki_occurrences()

    def __gen_matched_ens(self):
        """Gets all entities matching the n-gram"""
        if self.__matched_ens is None:
            matches = SF_WIKI.get(self.text)
            matched_ens = matches if matches is not None else {}
            self.__matched_ens = matched_ens
        return self.__matched_ens

    def __calc_wiki_occurrences(self):
        """Calculates the denominator for commonness (for Wiki annotations)."""
        if self.__wiki_occurrences is None:
            self.__wiki_occurrences = 0
            for en, occ in self.matched_ens.get('anchor', {}).iteritems():
                self.__wiki_occurrences += occ
        return self.__wiki_occurrences

    def get_men_candidate_ens(self, commonness_th):
        """
        Gets candidate entities for the given n-gram.

        :param commonness_th: commonness threshold
        :return: dictionary {Wiki_uri: commonness, ..}
        """
        candidate_entities = {}
        wiki_matches = self.get_wiki_matches(commonness_th)
        candidate_entities.update(wiki_matches)
        return candidate_entities

    def get_wiki_matches(self, commonness_th):
        """
        Gets entity matches from Wikipedia anchors (with dbpedia uris).

        :param commonness_th: float, Commonness threshold
        :return: Dictionary {Wiki_uri: commonness, ...}

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

    def calc_commonness(self, en_uri):
        """
        Calculates commonness for the given entity:
            (times mention is linked) / (times mention linked to entity)
            - Returns zero if the entity is not linked by the mention.

        :param en_uri: Wikipedia uri
        :return Commonness
        """
        if not en_uri.startswith("<wikipedia:"):
            raise Exception("Only Wikipedia URI should be passed to commonness!")
        cmn = self.matched_ens.get('anchor', {}).get(en_uri, 0) / float(self.wiki_occurrences)
        return cmn
