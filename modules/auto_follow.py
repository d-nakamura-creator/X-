"""自動フォローモジュール：キーワード検索・フォロワー・フォローバック。"""
import time
from datetime import datetime
from loguru import logger
from modules.client import get_client
from modules import state as st
import config


def _already_followed(state: dict, user_id: str) -> bool:
    return user_id in state.get("followed_users", {})


def _record_follow(state: dict, user_id: str) -> dict:
    state.setdefault("followed_users", {})[user_id] = datetime.now().isoformat()
    return st.increment(state, "follows")


def follow_by_keyword() -> None:
    """キーワード検索でツイートした人をフォローする。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
        logger.warning("[フォロー] 本日のフォロー上限に達しました")
        return

    client = get_client()
    for keyword in config.TARGET_KEYWORDS:
        if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
            break
        try:
            results = client.search_recent_tweets(
                query=f"{keyword} lang:ja -is:retweet",
                max_results=config.SEARCH_MAX_RESULTS,
                tweet_fields=["author_id"],
                expansions=["author_id"],
            )
            if not results.data:
                continue

            for tweet in results.data:
                uid = str(tweet.author_id)
                if uid == str(config.MY_USER_ID):
                    continue
                if _already_followed(state, uid):
                    continue
                if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
                    break

                try:
                    client.follow_user(
                        id=config.MY_USER_ID,
                        target_user_id=uid,
                    )
                    state = _record_follow(state, uid)
                    logger.success(f"[フォロー] keyword='{keyword}' user_id={uid}")
                    time.sleep(config.ACTION_INTERVAL)
                except Exception as e:
                    logger.error(f"[フォロー] 失敗 user_id={uid}: {e}")

        except Exception as e:
            logger.error(f"[フォロー] 検索失敗 keyword='{keyword}': {e}")


def follow_back_followers() -> None:
    """自分のフォロワーをフォローバックする。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
        logger.warning("[フォローバック] 本日のフォロー上限に達しました")
        return

    client = get_client()
    try:
        followers = client.get_users_followers(
            id=config.MY_USER_ID,
            max_results=100,
        )
        if not followers.data:
            return

        following = client.get_users_following(
            id=config.MY_USER_ID,
            max_results=1000,
        )
        following_ids = set()
        if following.data:
            following_ids = {str(u.id) for u in following.data}

        for user in followers.data:
            uid = str(user.id)
            if uid in following_ids:
                continue
            if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
                break

            try:
                client.follow_user(
                    id=config.MY_USER_ID,
                    target_user_id=uid,
                )
                state = _record_follow(state, uid)
                logger.success(f"[フォローバック] user_id={uid} (@{user.username})")
                time.sleep(config.ACTION_INTERVAL)
            except Exception as e:
                logger.error(f"[フォローバック] 失敗 user_id={uid}: {e}")

    except Exception as e:
        logger.error(f"[フォローバック] フォロワー取得失敗: {e}")


def follow_followers_of_influencers(influencer_ids: list[str]) -> None:
    """インフルエンサーのフォロワーをフォローする（ターゲット拡張）。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
        logger.warning("[インフルエンサーFF] 本日のフォロー上限に達しました")
        return

    client = get_client()
    for inf_id in influencer_ids:
        if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
            break
        try:
            followers = client.get_users_followers(
                id=inf_id,
                max_results=50,
            )
            if not followers.data:
                continue

            for user in followers.data:
                uid = str(user.id)
                if uid == str(config.MY_USER_ID):
                    continue
                if _already_followed(state, uid):
                    continue
                if not st.under_limit(state, "follows", config.FOLLOW_DAILY_LIMIT):
                    break

                try:
                    client.follow_user(
                        id=config.MY_USER_ID,
                        target_user_id=uid,
                    )
                    state = _record_follow(state, uid)
                    logger.success(f"[インフルエンサーFF] influencer={inf_id} user_id={uid}")
                    time.sleep(config.ACTION_INTERVAL)
                except Exception as e:
                    logger.error(f"[インフルエンサーFF] 失敗 user_id={uid}: {e}")

        except Exception as e:
            logger.error(f"[インフルエンサーFF] フォロワー取得失敗 inf_id={inf_id}: {e}")
