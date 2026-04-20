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
    "転職",
    "求人",
    "就職活動",
    "キャリアアップ",
]

# ── Indeed 雇用主アカウント認証情報 ───────────────────────────────────
INDEED_EMAIL    = os.getenv("INDEED_EMAIL", "")
INDEED_PASSWORD = os.getenv("INDEED_PASSWORD", "")

# ── Indeed 求人 URL（.env で上書き可能） ──────────────────────────────
INDEED_JOB_URL = os.getenv("INDEED_JOB_URL", "https://jp.indeed.com")

# ── Indeed アナリティクス最適化：何日間のデータを参照するか ──────────────
INDEED_ANALYTICS_DAYS = int(os.getenv("INDEED_ANALYTICS_DAYS", "7"))

# ── Playwright: ヘッドレスモード（True=バックグラウンド実行） ─────────────
INDEED_HEADLESS = os.getenv("INDEED_HEADLESS", "true").lower() == "true"

# ── 求職者検出キーワード（Indeed 誘導リプライのトリガー） ─────────────────
INDEED_KEYWORDS = [
    "転職したい",
    "仕事探してる",
    "求人 探してる",
    "就職活動 つらい",
    "転職活動 疲れた",
    "いい仕事 ない",
    "仕事 辞めたい",
    "正社員 なりたい",
    "パート 探してる",
    "アルバイト 探してる",
    "転職 悩んでる",
    "キャリアチェンジ",
    "求人 おすすめ",
    "転職 成功",
    "転職エージェント",
]

# ── Indeed 誘導リプライテンプレート ──────────────────────────────────
INDEED_REPLY_TEMPLATES = [
    "お仕事探しでお困りでしたら、Indeedに豊富な求人が揃っています✨ ぜひチェックしてみてください👇 {url}",
    "転職・求職中なんですね！Indeedなら全国の求人を一括検索できてとても便利ですよ🔍 {url}",
    "仕事探しはIndeedがおすすめです！条件を細かく絞り込めるので理想の求人が見つかりやすいです💼 {url}",
    "求人をお探しでしょうか？Indeedは掲載数No.1の求人サイトです。ぜひ一度見てみてください👀 {url}",
    "転職活動お疲れ様です🙌 Indeedを使うと効率よく求人を探せますよ！ {url}",
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
