"""自動いいねモジュール：キーワード検索結果・フォロワーのツイートにいいね。"""
import time
from loguru import logger
from modules.client import get_client
from modules import state as st
import config


def like_by_keyword() -> None:
    """キーワードでツイートを検索して自動いいね。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "likes", config.LIKE_DAILY_LIMIT):
        logger.warning("[いいね] 本日のいいね上限に達しました")
        return

    client = get_client()
    liked = set(state.get("liked_tweet_ids", []))

    for keyword in config.TARGET_KEYWORDS:
        if not st.under_limit(state, "likes", config.LIKE_DAILY_LIMIT):
            break
        try:
            results = client.search_recent_tweets(
                query=f"{keyword} lang:ja -is:retweet",
                max_results=config.SEARCH_MAX_RESULTS,
                tweet_fields=["author_id", "public_metrics"],
            )
            if not results.data:
                continue

            # エンゲージメントの高いツイートを優先
            tweets = sorted(
                results.data,
                key=lambda t: (t.public_metrics or {}).get("like_count", 0),
                reverse=True,
            )

            for tweet in tweets:
                if str(tweet.id) in liked:
                    continue
                if str(tweet.author_id) == str(config.MY_USER_ID):
                    continue
                if not st.under_limit(state, "likes", config.LIKE_DAILY_LIMIT):
                    break

                try:
                    client.like(
                        user_auth=True,
                        tweet_id=tweet.id,
                    )
                    liked.add(str(tweet.id))
                    state["liked_tweet_ids"] = list(liked)
                    state = st.increment(state, "likes")
                    logger.success(f"[いいね] keyword='{keyword}' tweet_id={tweet.id}")
                    time.sleep(config.ACTION_INTERVAL)
                except Exception as e:
                    logger.error(f"[いいね] 失敗 tweet_id={tweet.id}: {e}")

        except Exception as e:
            logger.error(f"[いいね] 検索失敗 keyword='{keyword}': {e}")


def like_followers_tweets() -> None:
    """フォロワーの最新ツイートにいいね（関係強化）。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "likes", config.LIKE_DAILY_LIMIT):
        logger.warning("[いいね] 本日のいいね上限に達しました")
        return

    client = get_client()
    liked = set(state.get("liked_tweet_ids", []))

    try:
        followers = client.get_users_followers(
            id=config.MY_USER_ID,
            max_results=50,
        )
        if not followers.data:
            return

        for user in followers.data:
            if not st.under_limit(state, "likes", config.LIKE_DAILY_LIMIT):
                break
            try:
                tweets = client.get_users_tweets(
                    id=user.id,
                    max_results=3,
                    exclude=["retweets", "replies"],
                )
                if not tweets.data:
                    continue

                for tweet in tweets.data:
                    if str(tweet.id) in liked:
                        continue
                    if not st.under_limit(state, "likes", config.LIKE_DAILY_LIMIT):
                        break
                    try:
                        client.like(user_auth=True, tweet_id=tweet.id)
                        liked.add(str(tweet.id))
                        state["liked_tweet_ids"] = list(liked)
                        state = st.increment(state, "likes")
                        logger.success(f"[いいね] フォロワー @{user.username} tweet_id={tweet.id}")
                        time.sleep(config.ACTION_INTERVAL)
                    except Exception as e:
                        logger.error(f"[いいね] 失敗 tweet_id={tweet.id}: {e}")

            except Exception as e:
                logger.error(f"[いいね] ツイート取得失敗 user_id={user.id}: {e}")

    except Exception as e:
        logger.error(f"[いいね] フォロワー取得失敗: {e}")
