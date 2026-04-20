"""アナリティクスモジュール：フォロワー数推移・日次レポートを記録する。"""
import json
import os
from datetime import datetime
from loguru import logger
from modules.client import get_client
from modules import state as st
import config

ANALYTICS_FILE = "data/analytics.json"


def _load_analytics() -> list:
    if not os.path.exists(ANALYTICS_FILE):
        return []
    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_analytics(data: list) -> None:
    os.makedirs(os.path.dirname(ANALYTICS_FILE), exist_ok=True)
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_daily_stats() -> None:
    """フォロワー数と当日の行動数を記録する。"""
    client = get_client()
    try:
        me = client.get_user(
            id=config.MY_USER_ID,
            user_fields=["public_metrics"],
        )
        if not me.data:
            return

        metrics = me.data.public_metrics
        state = st.load()
        daily = state.get("daily_counts", {})

        record = {
            "date": str(datetime.now().date()),
            "timestamp": datetime.now().isoformat(),
            "followers_count": metrics.get("followers_count", 0),
            "following_count": metrics.get("following_count", 0),
            "tweet_count": metrics.get("tweet_count", 0),
            "actions": {
                "follows":   daily.get("follows", 0),
                "unfollows": daily.get("unfollows", 0),
                "likes":     daily.get("likes", 0),
                "retweets":  daily.get("retweets", 0),
                "replies":   daily.get("replies", 0),
            },
        }

        analytics = _load_analytics()
        analytics.append(record)
        _save_analytics(analytics)

        logger.success(
            f"[アナリティクス] フォロワー数: {record['followers_count']} | "
            f"フォロー: {record['actions']['follows']} | "
            f"いいね: {record['actions']['likes']} | "
            f"RT: {record['actions']['retweets']}"
        )

    except Exception as e:
        logger.error(f"[アナリティクス] 取得失敗: {e}")


def print_summary() -> None:
    """直近7日間のサマリーをログ出力する。"""
    analytics = _load_analytics()
    if not analytics:
        logger.info("[アナリティクス] データなし")
        return

    recent = analytics[-7:]
    logger.info("=" * 50)
    logger.info("📊 直近7日間サマリー")
    logger.info("=" * 50)
    for r in recent:
        logger.info(
            f"{r['date']} | フォロワー: {r['followers_count']} | "
            f"F: {r['actions']['follows']} UF: {r['actions']['unfollows']} "
            f"L: {r['actions']['likes']} RT: {r['actions']['retweets']}"
        )
    if len(recent) >= 2:
        diff = recent[-1]["followers_count"] - recent[0]["followers_count"]
        logger.info(f"7日間フォロワー増減: {'+' if diff >= 0 else ''}{diff}")
    logger.info("=" * 50)
