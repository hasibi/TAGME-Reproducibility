"""
Wikipedia utils.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

from urllib import quote


class WikipediaUtils(object):
    mongo = None
    
    @staticmethod
    def wiki_title_to_uri(title):
        """
        Converts wiki page title to wiki_uri
        based on https://en.wikipedia.org/wiki/Wikipedia:Page_name#Spaces.2C_underscores_and_character_coding
        encoding based on http://dbpedia.org/services-resources/uri-encoding
        """
        if title:
            wiki_uri = "<wikipedia:" + quote(title, ' !$&\'()*+,-./:;=@_~').replace(' ', '_') + ">"
            return wiki_uri
        else:
            return None

    @staticmethod
    def wiki_uri_to_dbp_uri(wiki_uri):
        """Converts Wikipedia uri to DBpedia URI."""
        return wiki_uri.replace("<wikipedia:", "<dbpedia:")


def main():
    # example usage    
    print WikipediaUtils.wiki_title_to_uri("Tango (genre musical)")

if __name__ == "__main__":
    main()