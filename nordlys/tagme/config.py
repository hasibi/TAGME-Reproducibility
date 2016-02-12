"""
Configurations for tagme package.

@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

from nordlys.config import DATA_DIR
from nordlys.storage.surfaceforms import SurfaceForms


# Test collection files
Y_ERD = DATA_DIR + "/Y-ERD.tsv"

ERD_QUERY = DATA_DIR + "/Trec_beta.query.txt"
ERD_ANNOTATION = DATA_DIR + "/Trec_beta.annotation.txt"

WIKI_ANNOT30 = DATA_DIR + "/wiki-annot30"
WIKI_ANNOT30_SNIPPET = DATA_DIR + "/wiki-annot30-snippet.txt"
WIKI_ANNOT30_ANNOTATION = DATA_DIR + "/wiki-annot30-annotation.txt"

WIKI_DISAMB30 = DATA_DIR + "/wiki-disamb30"
WIKI_DISAMB30_SNIPPET = DATA_DIR + "/wiki-disamb30-snippet.txt"
WIKI_DISAMB30_ANNOTATION = DATA_DIR + "/wiki-disamb30-annotation.txt"

# Surface form dictionaries
COLLECTION_SURFACEFORMS_WIKI = "surfaceforms_wiki_20100408"
SF_WIKI = SurfaceForms(collection=COLLECTION_SURFACEFORMS_WIKI)


INDEX_PATH = "/xxx/20100408-index"
INDEX_ANNOT_PATH = "/xxx/20100408-index-annot/"