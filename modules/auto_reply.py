"""自動返信モジュール：メンションおよびキーワード検索結果に返信する。"""
import random
import time
from loguru import logger
from modules.client import get_client
from modules import state as st
import config


def reply_to_mentions() -> None:
    """未返信のメンションに自動返信する。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "replies", config.REPLY_DAILY_LIMIT):
        logger.warning("[返信] 本日の返信上限に達しました")
        return

    client = get_client()
    try:
        mentions = client.get_users_mentions(
            id=config.MY_USER_ID,
            max_results=10,
            tweet_fields=["author_id"],
        )
        if not mentions.data:
            logger.info("[返信] 未返信のメンションなし")
            return

        replied = set(state.get("replied_tweet_ids", []))
        for tweet in mentions.data:
            if str(tweet.id) in replied:
                continue
            if not st.under_limit(state, "replies", config.REPLY_DAILY_LIMIT):
                break

            reply_text = random.choice(config.REPLY_TEMPLATES)
            try:
                client.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=tweet.id,
                )
                replied.add(str(tweet.id))
                state["replied_tweet_ids"] = list(replied)
                state = st.increment(state, "replies")
                logger.success(f"[返信] メンション返信完了: tweet_id={tweet.id}")
                time.sleep(config.ACTION_INTERVAL)
            except Exception as e:
                logger.error(f"[返信] 失敗 tweet_id={tweet.id}: {e}")

    except Exception as e:
        logger.error(f"[返信] メンション取得失敗: {e}")


def reply_to_keyword_tweets() -> None:
    """キーワードでツイートを検索して返信する。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "replies", config.REPLY_DAILY_LIMIT):
        logger.warning("[返信] 本日の返信上限に達しました")
        return

    client = get_client()
    replied = set(state.get("replied_tweet_ids", []))

    for keyword in config.TARGET_KEYWORDS:
        if not st.under_limit(state, "replies", config.REPLY_DAILY_LIMIT):
            break
        try:
            results = client.search_recent_tweets(
                query=f"{keyword} lang:ja -is:retweet -is:reply",
                max_results=config.SEARCH_MAX_RESULTS,
                tweet_fields=["author_id"],
            )
            if not results.data:
                continue

            for tweet in results.data:
                if str(tweet.id) in replied:
                    continue
                if str(tweet.author_id) == str(config.MY_USER_ID):
                    continue
                if not st.under_limit(state, "replies", config.REPLY_DAILY_LIMIT):
                    break

                reply_text = random.choice(config.REPLY_TEMPLATES)
                try:
                    client.create_tweet(
                        text=reply_text,
                        in_reply_to_tweet_id=tweet.id,
                    )
                    replied.add(str(tweet.id))
                    state["replied_tweet_ids"] = list(replied)
                    state = st.increment(state, "replies")
                    logger.success(f"[返信] キーワード返信完了: '{keyword}' tweet_id={tweet.id}")
                    time.sleep(config.ACTION_INTERVAL)
                except Exception as e:
                    logger.error(f"[返信] 失敗 tweet_id={tweet.id}: {e}")

        except Exception as e:
            logger.error(f"[返信] 検索失敗 keyword='{keyword}': {e}")
