"""Indeed求人自動最適化 エントリーポイント。"""
import sys
import json
import schedule
import time
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)
logger.add("data/indeed.log", rotation="10 MB", retention="14 days", level="DEBUG", encoding="utf-8")


def _check_config() -> bool:
    import config
    if not config.INDEED_EMAIL or not config.INDEED_PASSWORD:
        logger.error("INDEED_EMAIL / INDEED_PASSWORD が未設定です")
        logger.error(".env ファイルに以下を追記してください:")
        logger.error("  INDEED_EMAIL=your@email.com")
        logger.error("  INDEED_PASSWORD=yourpassword")
        return False
    return True


def cmd_optimize(dry_run: bool = False) -> None:
    """求人最適化を1回実行する。"""
    from modules.indeed_optimizer import run_optimization
    result = run_optimization(dry_run=dry_run)
    if not result:
        return
    logger.info("=" * 50)
    logger.info("【最適化結果】")
    logger.info(f"  更新完了: {len(result.get('updated', []))}件 → {result.get('updated', [])}")
    logger.info(f"  変更不要: {len(result.get('skipped', []))}件")
    logger.info("【アナリティクスサマリー】")
    for a in result.get("analytics", []):
        logger.info(
            f"  {a['title']}: 表示={a['impressions']} クリック={a['clicks']} "
            f"応募={a['applies']} CTR={a['ctr']} CVR={a['conversion']}"
        )
    logger.info("=" * 50)


def cmd_analytics() -> None:
    """アナリティクスのみ取得して表示する（求人更新はしない）。"""
    cmd_optimize(dry_run=True)


def cmd_scheduler() -> None:
    """定期実行モード：毎日指定時刻にアナリティクス確認＋最適化を行う。"""
    logger.info("=" * 50)
    logger.info("Indeed自動最適化スケジューラー起動")
    logger.info("=" * 50)

    # 毎朝9時と毎夕18時に最適化実行
    schedule.every().day.at("09:00").do(cmd_optimize)
    schedule.every().day.at("18:00").do(cmd_optimize)
    logger.info("[スケジュール] 最適化: 09:00 / 18:00")

    # 起動直後に即時実行
    cmd_optimize()

    logger.info("スケジューラー待機中... (Ctrl+C で停止)")
    while True:
        schedule.run_pending()
        time.sleep(60)


def main() -> None:
    import os
    os.makedirs("data", exist_ok=True)

    if not _check_config():
        sys.exit(1)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "scheduler"

    match cmd:
        case "optimize":
            cmd_optimize()
        case "dry-run":
            cmd_optimize(dry_run=True)
        case "analytics":
            cmd_analytics()
        case "scheduler":
            cmd_scheduler()
        case _:
            print("""
Indeed求人自動最適化ツール

使い方:
  python indeed_main.py               # スケジューラー起動（09:00/18:00に自動実行）
  python indeed_main.py optimize      # 今すぐ最適化を実行
  python indeed_main.py dry-run       # 変更内容の確認のみ（実際の更新なし）
  python indeed_main.py analytics     # アナリティクスデータの表示のみ

事前準備（.envに追記）:
  INDEED_EMAIL=your@email.com
  INDEED_PASSWORD=yourpassword
  INDEED_JOB_URL=https://jp.indeed.com/jobs?q=...  # 任意
  INDEED_ANALYTICS_DAYS=7                           # 参照期間（7/14/30日）
  INDEED_HEADLESS=true                              # false にするとブラウザが表示される
""")


if __name__ == "__main__":
    main()
