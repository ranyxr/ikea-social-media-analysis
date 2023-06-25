#!/usr/bin/python3
"""
A BaseProcessor class that provide basic functions to interact with Mastodon API and the database.
"""

import logging
import time
import os

import mariadb
import requests
from datetime import datetime
from mastodon import Mastodon, StreamListener

LOGGER_NAME = "base_processor"


class BaseProcessor:
    """
    Basic functions including interacting with Mastodon API and the database and data cleaning.
    """

    def __init__(self):
        """
        Initialise the BaseProcessor.
        """
        self._logger = logging.getLogger(LOGGER_NAME)

        # Get ENV VAR parameters of mariadb
        # Get ENV VAR parameters of mariadb
        self.mariadb_host = os.environ["MARIADB_HOST"]
        self.mariadb_database = os.environ["MARIADB_DATABASE"]
        self.mariadb_user = os.environ["MARIADB_USER"]
        self.mariadb_password = os.environ["MARIADB_PASSWORD"]

        self.api_base_url = 'https://mastodon.online'
        self.access_token = os.getenv('MASTODON_TOKEN')

    def setup_mastodon_client(self):
        """
        Set up Mastodon client using Mastodon.py
        :return: Mastodon object
        """

        return Mastodon(
            access_token=self.access_token,
            api_base_url=self.api_base_url
        )

    # TODO: deduplicate before saving
    def deduplicate_posts(self):
        pass

    def connect_mariadb(self):
        """Connect to MariaDB Server"""
        try:
            conn = mariadb.connect(
                user=self.mariadb_user,
                password=self.mariadb_password,
                host=self.mariadb_host,
                port=3306,
                database=self.mariadb_database
            )
        except mariadb.Error as err:
            self._logger.error(f"Error connecting to MariaDB Platform: {err}")
            raise err

        return conn

    def save_post(self, post, post_table):
        """
        Save the Mastodon posts to the specific post_table
        """
        if post is None:
            return False

        conn = self.connect_mariadb()
        try:
            if type(post['created_at']) == str:
                created_at = datetime.strptime(post['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
            else:
                # API returns a datetime as created_at instead of a string
                created_at = post['created_at']

            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {post_table} (
                        mastodon_id,
                        created_at,
                        language,
                        uri,    
                        favourites_count,
                        text,
                        tags
                    ) VALUES (?,?,?,?,?,?,?)
                    """,
                    (post['mastodon_id'],
                    created_at,
                    post['language'],
                    post['uri'],
                    post['favourites_count'],
                    post['text'],
                    post['tags'])
                )
            self._logger.info(f'Successfully insert the post {post["mastodon_id"]}')
        except Exception as e:
            self._logger.error(e)
            self._logger.error(f'Cannot insert data into database. Trying to insert {post}')
        conn.commit()

    def get_latest_post_id(self, post_table):
        """
        Get the latest post id in the post table.
        :return: str: the latest post id
        """
        conn = self.connect_mariadb()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        id,
                        mastodon_id,
                        text,
                        created_at,
                        favourites_count,
                        language,
                        uri,
                        tags
                    FROM {post_table}
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
                return cursor.fetchone()
        except Exception as e:
            self._logger.error(e)
            self._logger.error(f'Cannot retrieve the latest records from {post_table}')
            return None
