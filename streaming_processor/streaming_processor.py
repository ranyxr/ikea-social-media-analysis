import requests
import time
import logging
from mastodon import Mastodon, StreamListener
from base_processor import BaseProcessor
from pprint import pprint

LOGGER_NAME = "streaming_processor"


class MyStreamListener(StreamListener, BaseProcessor):
    def __init__(self, post_table):
        super().__init__()
        self.post_table = post_table
        self._logger = logging.getLogger(LOGGER_NAME)
        self.start = time.time()

    def on_update(self, status):
        processed_post = self.process_post(status)
        if processed_post:
            self.save_to_database(processed_post)
        current = time.time()
        if current-self.start > 20:
            # Stop streaming after 20 seconds
            raise StopIteration('I have been running for 20 seconds, it is time to have a rest.')

    def process_post(self, post):
        # Process the retrieved data

        self._logger.info('Processing a post...')
        # Filter out bots
        if post['account']['bot']:
            return None
        processed_post = {
            'mastodon_id': post['id'],
            'created_at': post['created_at'],
            'language': post['language'],
            'uri': post['uri'],
            'favourites_count': post['favourites_count'],
            'text': post['content'],
            'tags': ','.join([tag['name'] for tag in post['tags']])
        }
        # pprint(processed_post)
        return processed_post

    def save_to_database(self, processed_post):
        self._logger.info('Saving a post...')
        self.save_post(processed_post, post_table=self.post_table)


class StreamingProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        # The table to save the posts by batch
        self.post_table = 'posts_streaming'
        self._logger = logging.getLogger(LOGGER_NAME)
        self.mastodon = Mastodon(
            access_token=self.access_token,
            api_base_url=self.api_base_url
        )
        self.listener = MyStreamListener(self.post_table)

    def run_streaming_processing(self, tag: str):
        self._logger.info('Start streaming...')
        # Start streaming public timeline
        # self.mastodon.stream_hashtag(tag=tag, listener=self.listener)

        # Streaming data for IKEA usually empty like the stream_hashtag above,
        # use the following function to test processing and saving functions.
        self.mastodon.stream_public(listener=self.listener)


if __name__ == '__main__':
    # Sleep 10 seconds, so in the future when stakeholders require performance improvement, you can fulfill it quickly
    # by removing the sleep. Just kidding, sleep to wait MariaDB fully ready.
    time.sleep(10)
    # Setup logging for the script
    logging.basicConfig(level=logging.INFO)
    # TODO: put the keywords in a DB table as configuration
    query_tags = ['IKEA']
    # TODO: to filter out the posts that contain the blacklist_keywords
    blacklist_keywords = ['discount', 'gratis', '甩卖']

    streaming_processor = StreamingProcessor()
    # batch from since_id
    for tag in query_tags:
        streaming_processor.run_streaming_processing(tag)
