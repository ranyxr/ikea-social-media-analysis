import pytest
from datetime import datetime
from batch_processor.batch_processor import BatchProcessor


@pytest.fixture
def batch_processor():
    return BatchProcessor()


def test_process_posts(batch_processor):
    # Create a sample list of posts
    posts = [
        {
            'mastodon_id': '12345',
            'created_at': datetime.now().isoformat(),
            'language': 'en',
            'uri': 'https://example.com/post/12345',
            'favourites_count': 10,
            'content': 'This is a test post',
            'tags': [{'name': 'test'}, {'name': 'post'}],
            'account': {'bot': False}
        },
        {
            'mastodon_id': '67890',
            'created_at': '2023-06-23T17:59:52.000Z',
            'language': 'en',
            'uri': 'https://example.com/post/67890',
            'favourites_count': 5,
            'content': 'Another test post',
            'tags': [{'name': 'test'}, {'name': 'post'}],
            'account': {'bot': False}
        },
        {
            'mastodon_id': 'abcde',
            'created_at': '2023-06-23T17:59:52.000Z',
            'language': 'en',
            'uri': 'https://example.com/post/67890',
            'favourites_count': 5,
            'content': 'Another test post',
            'tags': [{'name': 'test'}, {'name': 'batch'}],
            'account': {'bot': True}
        }
    ]

    # Call the process_posts method
    processed_posts = batch_processor.process_posts(posts)

    # Check if the processed posts match the expected output
    assert len(processed_posts) == len(posts)-1
    for i, processed_post in enumerate(processed_posts):
        assert processed_post['mastodon_id'] == posts[i]['mastodon_id']
        assert type(processed_post['created_at']) == datetime
        assert processed_post['language'] == posts[i]['language']
        assert processed_post['uri'] == posts[i]['uri']
        assert processed_post['favourites_count'] == posts[i]['favourites_count']
        assert processed_post['text'] == posts[i]['content']
        assert processed_post['tags'] == 'test,post'  # Tags are joined with commas
