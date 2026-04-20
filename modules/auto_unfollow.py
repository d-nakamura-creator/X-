"""自動アンフォローモジュール：一定日数フォローバックしない人をアンフォロー。"""
import time
from datetime import datetime, timedelta
from loguru import logger
from modules.client import get_client
from modules import state as st
import config


def unfollow_non_followers() -> None:
    """フォロー後 UNFOLLOW_AFTER_DAYS 日経ってもフォローバックしない人をアンフォロー。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if not st.under_limit(state, "unfollows", config.UNFOLLOW_DAILY_LIMIT):
        logger.warning("[アンフォロー] 本日のアンフォロー上限に達しました")
        return

    client = get_client()
    try:
        followers = client.get_users_followers(
            id=config.MY_USER_ID,
            max_results=1000,
        )
        follower_ids = set()
        if followers.data:
            follower_ids = {str(u.id) for u in followers.data}

        cutoff = datetime.now() - timedelta(days=config.UNFOLLOW_AFTER_DAYS)
        followed_users: dict = state.get("followed_users", {})
        to_unfollow = []

        for uid, followed_at_str in followed_users.items():
            try:
                followed_at = datetime.fromisoformat(followed_at_str)
            except ValueError:
                continue
            if followed_at < cutoff and uid not in follower_ids:
                to_unfollow.append(uid)

        if not to_unfollow:
            logger.info("[アンフォロー] アンフォロー対象なし")
            return

        for uid in to_unfollow:
            if not st.under_limit(state, "unfollows", config.UNFOLLOW_DAILY_LIMIT):
                break
            try:
                client.unfollow_user(
                    id=config.MY_USER_ID,
                    target_user_id=uid,
                )
                del state["followed_users"][uid]
                state = st.increment(state, "unfollows")
                logger.success(f"[アンフォロー] user_id={uid}")
                time.sleep(config.ACTION_INTERVAL)
            except Exception as e:
                logger.error(f"[アンフォロー] 失敗 user_id={uid}: {e}")

    except Exception as e:
        logger.error(f"[アンフォロー] フォロワー取得失敗: {e}")
