# -*- coding: utf-8 -*-
'''The Tuttosport feed fetcher

.. moduleauthor:: Jacques de Laval <chucky@wrutschkow.org>

'''
from time import sleep
import sys

from concurrent.futures import as_completed, ThreadPoolExecutor

import db
import log
import random
import settings
from sourcemodel.models import RssModel


class FeedFetcher(log.Logging):
    def __init__(self, executor, feeds, db_settings):
        super(FeedFetcher, self).__init__()
        self.executor = executor
        self.storage = db.Db(**db_settings)
        self.feeds = feeds

    def save_feeds(self):
        self.logger.info(
            'Fetching feeds: %s' % ', '.join(name for name in self.feeds))
        fetches_to_name = dict(self.fetch_feeds())
        for fetch in as_completed(fetches_to_name):
            name = fetches_to_name[fetch]
            try:
                entries = fetch.result()
            except Exception:
                self.logger.exception('%r generated an exception' % name)
            else:
                self.logger.info('Saving %s' % name)
                save = self.executor.submit(self.storage.save_entries, entries)
                yield save, name

    def fetch_feeds(self):
        '''Fetches a list of feeds and returns a list of feed entries

        Args:
            feeds: Dictionary of feeds.
        '''
        for name, feed in self.feeds.iteritems():
            fetch = self.executor.submit(self.fetch_feed, feed)
            yield fetch, name

    def fetch_feed(self, feed):
        '''Fetches a feed and return a list of feed entries
        '''
        filter_ = feed.get('filter')
        if filter_ is not None:
            return RssModel(source_url=feed['url'])|filter_
        return RssModel(source_url=feed['url'])


class App(log.Logging):
    def __init__(self):
        super(App, self).__init__()
        self.executor = ThreadPoolExecutor(settings.max_workers)

    def __enter__(self):
        self.feed_fetcher = FeedFetcher(self.executor,
                                        settings.feeds,
                                        settings.database)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            raise exc_value
        except SystemExit:
            self.logger.info('Exiting, bye bye')
        self.exit()

    def exit(self):
        self.executor.shutdown()

    def run(self):
        running = True
        while running:
            try:
                self._revolution()
                sleep(settings.resolution)
            except KeyboardInterrupt:
                running = False
        sys.exit()

    def _revolution(self):
        futures_to_name = dict(self.feed_fetcher.save_feeds())
        for saves in as_completed(futures_to_name):
            name = futures_to_name[saves]
            try:
                count = saves.result()
            except Exception:
                self.logger.exception('%r generated an exception' % name)
            else:
                self.logger.info('Saved %d entries from %s' % (count, name))

if __name__ == '__main__':
    with App() as app:
        app.run()
