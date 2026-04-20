"""スケジューラー：全モジュールを定期実行する。"""
import schedule
import time
from loguru import logger

from modules.auto_post import post_tweet
from modules.auto_reply import reply_to_mentions, reply_to_keyword_tweets, reply_to_job_seekers
from modules.auto_follow import follow_by_keyword, follow_back_followers
from modules.auto_unfollow import unfollow_non_followers
from modules.auto_like import like_by_keyword, like_followers_tweets
from modules.auto_retweet import retweet_by_keyword
from modules.trending import post_trend_tweet
from modules.analytics import record_daily_stats, print_summary
import config


def setup_schedules() -> None:
    # ── 自動投稿：設定した時刻に毎日 ──────────────────────────────
    for t in config.POST_TIMES:
        schedule.every().day.at(t).do(post_tweet)
        logger.info(f"[スケジュール] 自動投稿: {t}")

    # ── トレンド投稿：毎日12:30 ────────────────────────────────
    schedule.every().day.at("12:30").do(post_trend_tweet)
    logger.info("[スケジュール] トレンド投稿: 12:30")

    # ── メンション返信：30分ごと ───────────────────────────────
    schedule.every(30).minutes.do(reply_to_mentions)
    logger.info("[スケジュール] メンション返信: 30分ごと")

    # ── キーワード返信：2時間ごと ──────────────────────────────
    schedule.every(2).hours.do(reply_to_keyword_tweets)
    logger.info("[スケジュール] キーワード返信: 2時間ごと")

    # ── Indeed求人誘導返信：1時間ごと ─────────────────────────
    schedule.every(1).hours.do(reply_to_job_seekers)
    logger.info("[スケジュール] Indeed求人誘導返信: 1時間ごと")

    # ── キーワードフォロー：1時間ごと ─────────────────────────
    schedule.every(1).hours.do(follow_by_keyword)
    logger.info("[スケジュール] キーワードフォロー: 1時間ごと")

    # ── フォローバック：3時間ごと ──────────────────────────────
    schedule.every(3).hours.do(follow_back_followers)
    logger.info("[スケジュール] フォローバック: 3時間ごと")

    # ── アンフォロー：毎日02:00 ────────────────────────────────
    schedule.every().day.at("02:00").do(unfollow_non_followers)
    logger.info("[スケジュール] アンフォロー: 02:00")

    # ── いいね：1時間ごと ─────────────────────────────────────
    schedule.every(1).hours.do(like_by_keyword)
    logger.info("[スケジュール] キーワードいいね: 1時間ごと")

    # ── フォロワーいいね：4時間ごと ───────────────────────────
    schedule.every(4).hours.do(like_followers_tweets)
    logger.info("[スケジュール] フォロワーいいね: 4時間ごと")

    # ── リツイート：2時間ごと ─────────────────────────────────
    schedule.every(2).hours.do(retweet_by_keyword)
    logger.info("[スケジュール] リツイート: 2時間ごと")

    # ── アナリティクス記録：毎日23:50 ─────────────────────────
    schedule.every().day.at("23:50").do(record_daily_stats)
    schedule.every().day.at("23:55").do(print_summary)
    logger.info("[スケジュール] アナリティクス: 23:50/23:55")


def run() -> None:
    logger.info("=" * 50)
    logger.info("🚀 X自動化システム起動")
    logger.info("=" * 50)
    setup_schedules()
    logger.info("起動時に全アクションを初回実行します...")

    # 起動直後に即時実行
    post_tweet()
    reply_to_mentions()
    reply_to_job_seekers()
    follow_by_keyword()
    follow_back_followers()
    like_by_keyword()
    retweet_by_keyword()
    record_daily_stats()

    logger.info("スケジューラー待機中... (Ctrl+C で停止)")
    while True:
        schedule.run_pending()
        time.sleep(30)
