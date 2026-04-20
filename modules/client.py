import tweepy
import config

def get_client() -> tweepy.Client:
    """読み書き両用のTwitter API v2クライアントを返す。"""
    return tweepy.Client(
        bearer_token=config.BEARER_TOKEN,
        consumer_key=config.API_KEY,
        consumer_secret=config.API_SECRET,
        access_token=config.ACCESS_TOKEN,
        access_token_secret=config.ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )
