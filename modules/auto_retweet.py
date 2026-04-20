"""自動リツイートモジュール：キーワード検索結果の高エンゲージメントツイートをRT。"""
import time
from loguru import logger
from modules.client import get_client
from modules import state as st
import config


def retweet_by_keyword() -> None:
    """キーワードで高エンゲージメントのツイートを自動リツイート。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "retweets", config.RETWEET_DAILY_LIMIT):
        logger.warning("[RT] 本日のリツイート上限に達しました")
        return

    client = get_client()
    retweeted = set(state.get("retweeted_tweet_ids", []))

    for keyword in config.TARGET_KEYWORDS:
        if not st.under_limit(state, "retweets", config.RETWEET_DAILY_LIMIT):
            break
        try:
            results = client.search_recent_tweets(
                query=f"{keyword} lang:ja -is:retweet min_faves:50",
                max_results=config.SEARCH_MAX_RESULTS,
                tweet_fields=["author_id", "public_metrics"],
            )
            if not results.data:
                continue

            tweets = sorted(
                results.data,
                key=lambda t: (t.public_metrics or {}).get("retweet_count", 0),
                reverse=True,
            )

            for tweet in tweets[:3]:  # キーワードごとに最大3件
                if str(tweet.id) in retweeted:
                    continue
                if str(tweet.author_id) == str(config.MY_USER_ID):
                    continue
                if not st.under_limit(state, "retweets", config.RETWEET_DAILY_LIMIT):
                    break

                try:
                    client.retweet(
                        user_auth=True,
                        tweet_id=tweet.id,
                    )
                    retweeted.add(str(tweet.id))
                    state["retweeted_tweet_ids"] = list(retweeted)
                    state = st.increment(state, "retweets")
                    logger.success(f"[RT] keyword='{keyword}' tweet_id={tweet.id}")
                    time.sleep(config.ACTION_INTERVAL)
                except Exception as e:
                    logger.error(f"[RT] 失敗 tweet_id={tweet.id}: {e}")

        except Exception as e:
            logger.error(f"[RT] 検索失敗 keyword='{keyword}': {e}")
