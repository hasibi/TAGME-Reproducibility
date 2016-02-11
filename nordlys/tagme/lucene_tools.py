"""
Tools for Lucene.
All Lucene features should be accessed in nordlys through this class. 

- Lucene class for ensuring that the same version, analyzer, etc. 
  are used across nordlys modules. Handles IndexReader, IndexWriter, etc.  
- Command line tools for checking indexed document content

@author: Krisztian Balog (krisztian.balog@uis.no)
@author: Faegheh Hasibi (faegheh.hasibi@idi.ntnu.no)
"""

import argparse
import lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document
from org.apache.lucene.document import Field
from org.apache.lucene.document import FieldType
from org.apache.lucene.index import IndexWriter
from org.apache.lucene.index import IndexWriterConfig
from org.apache.lucene.index import DirectoryReader 
from org.apache.lucene.index import Term
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search import TermQuery
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import PhraseQuery
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.store import IOContext

# has java VM for Lucene been initialized
lucene_vm_init = False


class Lucene(object):

    # default fieldnames for id and contents
    FIELDNAME_ID = "id"
    FIELDNAME_CONTENTS = "contents"

    # internal fieldtypes
    # used as Enum, the actual values don't matter
    FIELDTYPE_ID = "id"
    FIELDTYPE_ID_TV = "id_tv"
    FIELDTYPE_TEXT = "text"
    FIELDTYPE_TEXT_TV = "text_tv"
    FIELDTYPE_TEXT_TVP = "text_tvp"

    def __init__(self, index_dir, use_ram=False, jvm_ram=None):
        global lucene_vm_init
        if not lucene_vm_init:
            if jvm_ram:
                # e.g. jvm_ram = "8g"
                print "Increased JVM ram"
                lucene.initVM(vmargs=['-Djava.awt.headless=true'], maxheap=jvm_ram)
            else:
                lucene.initVM(vmargs=['-Djava.awt.headless=true'])
            lucene_vm_init = True
        self.dir = SimpleFSDirectory(File(index_dir))

        self.use_ram = use_ram
        if use_ram:
            print "Using ram directory..."
            self.ram_dir = RAMDirectory(self.dir, IOContext.DEFAULT)
        self.analyzer = None
        self.reader = None
        self.searcher = None
        self.writer = None
        self.ldf = None
        print "Connected to index " + index_dir

    def get_version(self):
        """Get Lucene version."""
        return Version.LUCENE_48

    def get_analyzer(self):
        """Get analyzer."""
        if self.analyzer is None:
            self.analyzer = StandardAnalyzer(self.get_version())
        return self.analyzer

    def open_reader(self):
        """Open IndexReader."""
        if self.reader is None:
            if self.use_ram:
                print "reading from ram directory ..."
                self.reader = DirectoryReader.open(self.ram_dir)
            else:
                self.reader = DirectoryReader.open(self.dir)

    def get_reader(self):
        return self.reader

    def close_reader(self):
        """Close IndexReader."""
        if self.reader is not None:
            self.reader.close()
            self.reader = None
        else:
            raise Exception("There is no open IndexReader to close")

    def open_searcher(self):
        """
        Open IndexSearcher. Automatically opens an IndexReader too,
        if it is not already open. There is no close method for the
        searcher.
        """
        if self.searcher is None:
            self.open_reader()
            self.searcher = IndexSearcher(self.reader)

    def get_searcher(self):
        """Returns index searcher (opens it if needed)."""
        self.open_searcher()
        return self.searcher

    def open_writer(self):
        """Open IndexWriter."""
        if self.writer is None:
            config = IndexWriterConfig(self.get_version(), self.get_analyzer())
            config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
            self.writer = IndexWriter(self.dir, config)
        else:
            raise Exception("IndexWriter is already open")

    def close_writer(self):
        """Close IndexWriter."""
        if self.writer is not None:
            self.writer.close()
            self.writer = None
        else:
            raise Exception("There is no open IndexWriter to close")

    def add_document(self, contents):
        """
        Adds a Lucene document with the specified contents to the index.
        See LuceneDocument.create_document() for the explanation of contents.
        """
        if self.ldf is None:  # create a single LuceneDocument object that will be reused
            self.ldf = LuceneDocument()
        self.writer.addDocument(self.ldf.create_document(contents))

    def get_lucene_document_id(self, doc_id):
        """Loads a document from a Lucene index based on its id."""
        self.open_searcher()
        query = TermQuery(Term(self.FIELDNAME_ID, doc_id))
        tophit = self.searcher.search(query, 1).scoreDocs
        if len(tophit) == 1:
            return tophit[0].doc
        else:
            return None

    def get_document_id(self, lucene_doc_id):
        """Gets lucene document id and returns the document id."""
        self.open_reader()
        return self.reader.document(lucene_doc_id).get(self.FIELDNAME_ID)

    def get_id_lookup_query(self, id, field=None):
        """Creates Lucene query for searching by (external) document id """
        if field is None:
            field = self.FIELDNAME_ID
        return TermQuery(Term(field, id))

    def get_and_query(self, queries):
        """Creates an AND Boolean query from multiple Lucene queries """
        # empty boolean query with Similarity.coord() disabled
        bq = BooleanQuery(False)
        for q in queries:
            bq.add(q, BooleanClause.Occur.MUST)
        return bq

    def get_or_query(self, queries):
        """Creates an OR Boolean query from multiple Lucene queries """
        # empty boolean query with Similarity.coord() disabled
        bq = BooleanQuery(False)
        for q in queries:
            bq.add(q, BooleanClause.Occur.SHOULD)
        return bq

    def get_phrase_query(self, query, field):
        """Creates phrase query for searching exact phrase."""
        phq = PhraseQuery()
        for t in query.split():
            phq.add(Term(field, t))
        return phq

    def num_docs(self):
        """Returns number of documents in the index."""
        self.open_reader()
        return self.reader.numDocs()


class LuceneDocument(object):
    """Internal representation of a Lucene document"""

    def __init__(self):
        self.ldf = LuceneDocumentField()

    def create_document(self, contents):
        """Create a Lucene document from the specified contents.
        Contents is a list of fields to be indexed, represented as a dictionary
        with keys 'field_name', 'field_type', and 'field_value'."""
        doc = Document()
        for f in contents:
            doc.add(Field(f['field_name'], f['field_value'],
                          self.ldf.get_field(f['field_type'])))
        return doc


class LuceneDocumentField(object):
    """Internal handler class for possible field types"""

    def __init__(self):
        """Init possible field types"""

        # FIELD_ID: stored, indexed, non-tokenized
        self.field_id = FieldType()
        self.field_id.setIndexed(True)
        self.field_id.setStored(True)
        self.field_id.setTokenized(False)

        # FIELD_ID_TV: stored, indexed, not tokenized, with term vectors (without positions)
        # for storing IDs with term vector info
        self.field_id_tv = FieldType()
        self.field_id_tv.setIndexed(True)
        self.field_id_tv.setStored(True)
        self.field_id_tv.setTokenized(False)
        self.field_id_tv.setStoreTermVectors(True)

        # FIELD_TEXT: stored, indexed, tokenized, with positions
        self.field_text = FieldType()
        self.field_text.setIndexed(True)
        self.field_text.setStored(True)
        self.field_text.setTokenized(True)

        # FIELD_TEXT_TV: stored, indexed, tokenized, with term vectors (without positions)
        self.field_text_tv = FieldType()
        self.field_text_tv.setIndexed(True)
        self.field_text_tv.setStored(True)
        self.field_text_tv.setTokenized(True)
        self.field_text_tv.setStoreTermVectors(True)

        # FIELD_TEXT_TVP: stored, indexed, tokenized, with term vectors and positions
        # (but no character offsets)
        self.field_text_tvp = FieldType()
        self.field_text_tvp.setIndexed(True)
        self.field_text_tvp.setStored(True)
        self.field_text_tvp.setTokenized(True)
        self.field_text_tvp.setStoreTermVectors(True)
        self.field_text_tvp.setStoreTermVectorPositions(True)

    def get_field(self, type):
        """Get Lucene FieldType object for the corresponding internal FIELDTYPE_ value"""
        if type == Lucene.FIELDTYPE_ID:
            return self.field_id
        elif type == Lucene.FIELDTYPE_ID_TV:
            return self.field_id_tv
        elif type == Lucene.FIELDTYPE_TEXT:
            return self.field_text
        elif type == Lucene.FIELDTYPE_TEXT_TV:
            return self.field_text_tv
        elif type == Lucene.FIELDTYPE_TEXT_TVP:
            return self.field_text_tvp
        else:
            raise Exception("Unknown field type")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--index", help="index directory", type=str)
    args = parser.parse_args()

    index_dir = args.index
    print "Index:       " + index_dir + "\n"

    l = Lucene(index_dir, jvm_ram="8g")
    pq = l.get_phrase_query("originally used", "contents")

    l.open_searcher()
    tophit = l.searcher.search(pq, 1).scoreDocs
    print tophit[0]

if __name__ == '__main__':
    main()