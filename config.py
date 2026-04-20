import os
from dotenv import load_dotenv

load_dotenv()

# ── API 認証 ──────────────────────────────────────────────
API_KEY             = os.getenv("API_KEY", "")
API_SECRET          = os.getenv("API_SECRET", "")
ACCESS_TOKEN        = os.getenv("ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "")
BEARER_TOKEN        = os.getenv("BEARER_TOKEN", "")
MY_USER_ID          = os.getenv("MY_USER_ID", "")

# ── ターゲットキーワード（フォロー・いいね・リツイート対象） ───────────────
TARGET_KEYWORDS = [
    "Python",
    "プログラミング",
    "AI",
    "機械学習",
    "副業",
    "ビジネス",
]

# ── 投稿スケジュール（毎日 HH:MM） ───────────────────────────
POST_TIMES = ["07:00", "12:00", "18:00", "21:30"]

# ── レート制限（1日の上限。安全マージンを設けた保守的な値） ───────────────
FOLLOW_DAILY_LIMIT    = 150   # API上限400、余裕を持って150
UNFOLLOW_DAILY_LIMIT  = 150
LIKE_DAILY_LIMIT      = 400   # API上限1000
RETWEET_DAILY_LIMIT   = 80
REPLY_DAILY_LIMIT     = 40

# ── アンフォロー基準（フォロー後この日数経過してもフォローバックなし） ────
UNFOLLOW_AFTER_DAYS = 3

# ── 1操作ごとのインターバル（秒）─────────────────────────────
ACTION_INTERVAL = 5

# ── 検索結果の最大取得数 ─────────────────────────────────────
SEARCH_MAX_RESULTS = 20

# ── 自動返信テンプレート ──────────────────────────────────────
REPLY_TEMPLATES = [
    "ありがとうございます！参考になりました😊",
    "素晴らしい投稿ですね！フォローさせていただきました✨",
    "いつも勉強になります！",
    "共感します！これからもよろしくお願いします🙌",
]

# ── 自動投稿コンテンツ（posts.json が空の場合のフォールバック） ────────────
DEFAULT_POSTS = [
    "今日も一日頑張りましょう！💪 #モチベーション #成長",
    "小さな一歩が大きな変化を生む。継続は力なり🔥 #習慣化",
    "インプットとアウトプットのバランスが成長の鍵✨ #学習",
    "失敗は成功のもと。今日の経験が明日の力になる💡 #挑戦",
    "目標を明確にすることで行動が変わる🎯 #目標設定",
    "感謝の気持ちを忘れずに。今日もありがとう🙏 #感謝",
    "コツコツ積み上げることが最強の戦略📈 #継続",
]

# ── トレンド投稿テンプレート ──────────────────────────────────
TREND_POST_TEMPLATE = "【トレンド】{trend} が話題です！みなさんはどう思いますか？🤔 #{hashtag}"

# ── state.json のパス ─────────────────────────────────────
STATE_FILE = "data/state.json"
POSTS_FILE = "data/posts.json"
