"""トレンド活用モジュール：トレンドを取得しておすすめ投稿を生成する。"""
import random
import re
from loguru import logger
from modules.client import get_client
from modules.auto_post import post_tweet
import config

# Twitter API v2 でトレンドを取得する woeid（日本=23424856）
JAPAN_WOEID = 23424856


def _clean_hashtag(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\u3040-\u9FFF]", "", text)


def post_trend_tweet() -> None:
    """日本のトレンドトップ5からランダムに選んで投稿する。"""
    client = get_client()
    try:
        # v1 API でトレンド取得（v2未対応のためlegacyを使用）
        auth = _get_v1_api()
        trends = auth.get_place_trends(JAPAN_WOEID)[0]["trends"]
        # ツイート数でソート
        trends_sorted = sorted(
            [t for t in trends if t.get("tweet_volume")],
            key=lambda t: t["tweet_volume"] or 0,
            reverse=True,
        )
        if not trends_sorted:
            logger.info("[トレンド] トレンド取得結果なし")
            return

        trend = random.choice(trends_sorted[:5])
        trend_name = trend["name"]
        hashtag = _clean_hashtag(trend_name.lstrip("#"))

        text = config.TREND_POST_TEMPLATE.format(
            trend=trend_name,
            hashtag=hashtag,
        )
        post_tweet(text)
        logger.success(f"[トレンド] トレンド投稿: {trend_name}")

    except Exception as e:
        logger.error(f"[トレンド] 失敗: {e}")


def _get_v1_api():
    """Twitter API v1.1 クライアントを返す（トレンド取得用）。"""
    import tweepy
    auth = tweepy.OAuth1UserHandler(
        config.API_KEY,
        config.API_SECRET,
        config.ACCESS_TOKEN,
        config.ACCESS_TOKEN_SECRET,
    )
    return tweepy.API(auth)
