import requests
import time
import logging
from base_processor import BaseProcessor
from pprint import pprint

LOGGER_NAME = "batch_processor"


class BatchProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(LOGGER_NAME)
        # The table to save the posts by batch
        self.post_table = 'posts_batch'

    def fetch_posts_batch(self, query, batch_size, since_id):
        # Make API request to fetch data
        query_url = f"{self.api_base_url}/api/v1/timelines/tag/{query}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "ikeabot"
        }
        params = {
            'limit': str(batch_size)
        }
        # String. Return results newer than ID.
        if since_id:
            params['since_id'] = since_id
        response = requests.get(query_url, headers=headers, params=params)
        posts_batch = response.json()
        return posts_batch

    def process_posts(self, posts):
        # Process the retrieved data
        processed_posts = []
        for post in posts:
            # Filter out bots
            if post['account']['bot']:
                continue
            processed_post = {
                'mastodon_id': post['id'],
                'created_at': post['created_at'],
                'language': post['language'],
                'uri': post['uri'],
                'favourites_count': post['favourites_count'],
                'text': post['content'],
                'tags': ','.join([tag['name'] for tag in post['tags']])
            }
            processed_posts.append(processed_post)
        # pprint(processed_posts)
        return processed_posts

    def save_to_database(self, processed_posts):
        for post in processed_posts:
            self.save_post(post, post_table=self.post_table)

    def run_batch_processing(self, query, batch_size, total_batches):
        for batch_num in range(total_batches):
            # Get the latest post id from database, and query new data from there
            latest_post_id = self.get_latest_post_id(self.post_table)

            # Fetch data batch
            posts = self.fetch_posts_batch(query, batch_size, latest_post_id)

            # Process data
            processed_posts = self.process_posts(posts)
            self.save_to_database(processed_posts)

            # Add a delay between batches to avoid overwhelming the API
            time.sleep(1)

            self._logger.info(f"Batch {batch_num + 1} processed and saved.")

        self._logger.info("Batch processing completed.")


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

    batch_processor = BatchProcessor()
    # batch from since_id
    for tag in query_tags:
        batch_processor.run_batch_processing(tag, 5, 2)
