import json
import os
from datetime import date
from loguru import logger
import config


def load() -> dict:
    if not os.path.exists(config.STATE_FILE):
        return _default()
    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(state: dict) -> None:
    os.makedirs(os.path.dirname(config.STATE_FILE), exist_ok=True)
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def reset_daily_if_needed(state: dict) -> dict:
    today = str(date.today())
    if state["daily_counts"]["date"] != today:
        logger.info(f"日次カウントをリセット: {today}")
        state["daily_counts"] = {
            "date": today,
            "follows": 0,
            "unfollows": 0,
            "likes": 0,
            "retweets": 0,
            "replies": 0,
        }
        save(state)
    return state


def increment(state: dict, action: str) -> dict:
    state["daily_counts"][action] = state["daily_counts"].get(action, 0) + 1
    save(state)
    return state


def under_limit(state: dict, action: str, limit: int) -> bool:
    return state["daily_counts"].get(action, 0) < limit


def _default() -> dict:
    return {
        "followed_users": {},
        "replied_tweet_ids": [],
        "liked_tweet_ids": [],
        "retweeted_tweet_ids": [],
        "post_index": 0,
        "daily_counts": {
            "date": "",
            "follows": 0,
            "unfollows": 0,
            "likes": 0,
            "retweets": 0,
            "replies": 0,
        },
    }
