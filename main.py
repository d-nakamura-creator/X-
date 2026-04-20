"""X自動化システム エントリーポイント。"""
import sys
import os
from loguru import logger

# ログ設定
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("data/bot.log", rotation="10 MB", retention="14 days", level="DEBUG", encoding="utf-8")

os.makedirs("data", exist_ok=True)


def check_config() -> bool:
    import config
    missing = []
    for var in ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET", "BEARER_TOKEN", "MY_USER_ID"]:
        if not getattr(config, var):
            missing.append(var)
    if missing:
        logger.error(f"未設定の環境変数があります: {', '.join(missing)}")
        logger.error(".env ファイルを作成して設定してください（.env.example 参照）")
        return False
    return True


def main() -> None:
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        _run_single_command(cmd)
        return

    if not check_config():
        sys.exit(1)

    from scheduler import run
    run()


def _run_single_command(cmd: str) -> None:
    """コマンドライン引数による単発実行。"""
    if not check_config():
        sys.exit(1)

    match cmd:
        case "post":
            from modules.auto_post import post_tweet
            text = " ".join(sys.argv[2:]) or None
            post_tweet(text)

        case "reply-mentions":
            from modules.auto_reply import reply_to_mentions
            reply_to_mentions()

        case "reply-keywords":
            from modules.auto_reply import reply_to_keyword_tweets
            reply_to_keyword_tweets()

        case "reply-indeed":
            from modules.auto_reply import reply_to_job_seekers
            reply_to_job_seekers()

        case "follow":
            from modules.auto_follow import follow_by_keyword
            follow_by_keyword()

        case "follow-back":
            from modules.auto_follow import follow_back_followers
            follow_back_followers()

        case "unfollow":
            from modules.auto_unfollow import unfollow_non_followers
            unfollow_non_followers()

        case "like":
            from modules.auto_like import like_by_keyword
            like_by_keyword()

        case "retweet":
            from modules.auto_retweet import retweet_by_keyword
            retweet_by_keyword()

        case "trend":
            from modules.trending import post_trend_tweet
            post_trend_tweet()

        case "stats":
            from modules.analytics import record_daily_stats, print_summary
            record_daily_stats()
            print_summary()

        case _:
            print(f"""
X自動化システム

使い方:
  python main.py              # スケジューラー起動（フル自動）

単発コマンド:
  python main.py post [テキスト]   # ツイート投稿
  python main.py reply-mentions    # メンション返信
  python main.py reply-keywords    # キーワード返信
  python main.py reply-indeed      # Indeed求人誘導返信
  python main.py follow            # キーワードフォロー
  python main.py follow-back       # フォローバック
  python main.py unfollow          # アンフォロー
  python main.py like              # いいね
  python main.py retweet           # リツイート
  python main.py trend             # トレンド投稿
  python main.py stats             # 統計記録・表示
""")


if __name__ == "__main__":
    main()
