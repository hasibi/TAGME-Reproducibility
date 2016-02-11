"""
Entity surface forms stored in MongoDB.

The surface form is used as _id. The associated entities are stored in key-value format.

@author: Krisztian Balog (krisztian.balog@uis.no)
"""

from nordlys.config import MONGO_DB, MONGO_HOST
from nordlys.storage.mongo import Mongo


class SurfaceForms(object):

    def __init__(self, collection):
        self.collection = collection
        self.mongo = Mongo(MONGO_HOST, MONGO_DB, self.collection)

    def get(self, surface_form):
        """Returns all information associated with a surface form."""

        # need to unescape the keys in the value part
        mdoc = self.mongo.find_by_id(surface_form)
        if mdoc is None:
            return None
        doc = {}
        for f in mdoc:
            if f != Mongo.ID_FIELD:
                doc[f] = {}
                for key, value in mdoc[f].iteritems():
                    doc[f][Mongo.unescape(key)] = value

        return doc