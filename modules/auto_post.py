"""自動投稿モジュール：posts.json のツイートをローテーションで投稿する。"""
import json
import os
import random
from loguru import logger
from modules.client import get_client
from modules import state as st
import config


def _load_posts() -> list[str]:
    if os.path.exists(config.POSTS_FILE):
        with open(config.POSTS_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)
        if posts:
            return posts
    return config.DEFAULT_POSTS


def post_tweet(text: str | None = None) -> None:
    """1ツイートを投稿する。text 未指定時はローテーションから選択。"""
    state = st.load()
    state = st.reset_daily_if_needed(state)

    if text is None:
        posts = _load_posts()
        idx = state.get("post_index", 0) % len(posts)
        text = posts[idx]
        state["post_index"] = idx + 1
        st.save(state)

    client = get_client()
    try:
        resp = client.create_tweet(text=text)
        tweet_id = resp.data["id"]
        logger.success(f"[投稿] ツイート完了: id={tweet_id} | {text[:40]}...")
    except Exception as e:
        logger.error(f"[投稿] 失敗: {e}")


def post_thread(texts: list[str]) -> None:
    """複数テキストをスレッドとして投稿する。"""
    client = get_client()
    reply_to = None
    for i, text in enumerate(texts):
        try:
            kwargs = {"text": text}
            if reply_to:
                kwargs["in_reply_to_tweet_id"] = reply_to
            resp = client.create_tweet(**kwargs)
            reply_to = resp.data["id"]
            logger.success(f"[スレッド {i+1}/{len(texts)}] 投稿完了")
        except Exception as e:
            logger.error(f"[スレッド {i+1}] 失敗: {e}")
            break
