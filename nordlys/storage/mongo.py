"""
Tools for working with MongoDB.

@author: Krisztian Balog (krisztian.balog@uis.no)
"""

from pymongo import MongoClient


class Mongo(object):
    """Manages the MongoDB connection and operations."""
    ID_FIELD = "_id"

    def __init__(self, host, db, collection):
        self.client = MongoClient(host)
        self.db = self.client[db]
        self.collection = self.db[collection]
        self.db_name = db
        self.collection_name = collection
        print "Connected to " + self.db_name + "." + self.collection_name

    @staticmethod
    def escape(s):
        """Escapes string (to be used as key or fieldname).
        Replaces . and $ with their unicode eqivalents."""
        return s.replace(".", "\u002e").replace("$", "\u0024")

    @staticmethod
    def unescape(s):
        """Unescapes string."""
        return s.replace("\u002e", ".").replace("\u0024", "$")

    def find_by_id(self, doc_id):
        """Returns all document content for a given document id."""
        return self.get_doc(self.collection.find_one({Mongo.ID_FIELD: self.escape(doc_id)}))

    def get_doc(self, mdoc):
        """Returns document contents with with keys and _id field unescaped."""
        if mdoc is None:
            return None

        doc = {}
        for f in mdoc:
            if f == Mongo.ID_FIELD:
                doc[f] = self.unescape(mdoc[f])
            else:
                doc[self.unescape(f)] = mdoc[f]

        return doc

    @staticmethod
    def print_doc(doc):
        print "_id: " + doc[Mongo.ID_FIELD]
        for key, value in doc.iteritems():
            if key == Mongo.ID_FIELD: continue  # ignore the id key
            if type(value) is list:
                print key + ":"
                for v in value:
                    print "\t" + str(v)
            else:
                print key + ": " + str(value)