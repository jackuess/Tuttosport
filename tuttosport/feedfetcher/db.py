import random

import pymongo

import log

class Db(log.Logging):
    def __init__(self, name, collection, host='localhost', port=27017):
        super(Db, self).__init__()
        self._client = pymongo.MongoClient(host, port)
        
        self._news = self._client[name][collection]

    def __del__(self):
        self._client.close()

    def save_entries(self, entries):
        '''Saves entries in a MongoDB database. Entries whos _id already exists
           gets updated.

        Args:
            entries: The entries to save.

        Returns:
            The number of entries updated/inserted
        '''
        for count, e in enumerate(entries):
            e['_id'] = e['link']
            self._news.save(e)
        return count

    def get_entries(self):
        return self._news.find().sort('pub_date', pymongo.DESCENDING)
