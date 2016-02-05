"""
erd global econfig

"""

from os import path
from nordlys.wikipedia.config import COLLECTION_SURFACEFORMS_WIKI_2010, COLLECTION_SURFACEFORMS_WIKI_2012
from nordlys.entity.surfaceforms import SurfaceForms

OUTPUT_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) + "/output"
DATA_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) + "/data/"

Y_ERD = DATA_DIR + "/tagme/Y-ERD.tsv"
ERD_QUERY = DATA_DIR + "/tagme/Trec_beta.query.txt"
ERD_ANNOTATION = DATA_DIR + "/tagme/Trec_beta.annotation.txt"

WIKI_ANNOT30 = DATA_DIR + "/tagme/wiki-annot30"
WIKI_ANNOT30_SNIPPET = DATA_DIR + "/tagme/wiki-annot30-snippet.txt"
WIKI_ANNOT30_ANNOTATION = DATA_DIR + "/tagme/wiki-annot30-annotation.txt"

WIKI_DISAMB30 = DATA_DIR + "/tagme/wiki-disamb30"
WIKI_DISAMB30_SNIPPET = DATA_DIR + "/tagme/wiki-disamb30-snippet.txt"
WIKI_DISAMB30_ANNOTATION = DATA_DIR + "/tagme/wiki-disamb30-annotation.txt"



SF = SurfaceForms(lowercase=True)
SF_WIKI10 = SurfaceForms(collection=COLLECTION_SURFACEFORMS_WIKI_2010)
# SF_WIKI12 = SurfaceForms(collection=COLLECTION_SURFACEFORMS_WIKI_2012)


