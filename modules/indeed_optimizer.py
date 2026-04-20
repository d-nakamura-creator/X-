"""Indeed求人最適化モジュール：アナリティクスを取得し求人内容を自動改善する。"""
import time
from dataclasses import dataclass
from loguru import logger
from playwright.sync_api import sync_playwright, Page, TimeoutError as PWTimeout
import config

_LOGIN_URL     = "https://secure.indeed.com/account/login"
_ANALYTICS_URL = "https://employers.indeed.com/p/analytics"


@dataclass
class JobAnalytics:
    job_id: str
    title: str
    clicks: int = 0
    applies: int = 0
    impressions: int = 0
    ctr: float = 0.0        # clicks / impressions
    conversion: float = 0.0  # applies / clicks
    description: str = ""


def _login(page: Page) -> bool:
    """Indeedにログインする。自動で失敗したら手動ログインを待機する。"""
    try:
        page.goto(_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # 手動ログインモードはすぐ手動へ
        if config.INDEED_LOGIN_MODE == "manual":
            logger.info("[Indeed] 手動ログインモードで起動中")
            return _wait_manual_login(page)

        # ── ステップ1: メールアドレス入力 ──────────────────────
        email_input = page.wait_for_selector(
            'input[type="email"], input[name="__email"]',
            timeout=10000,
        )
        email_input.fill(config.INDEED_EMAIL)
        page.click('button:has-text("続ける"), button[type="submit"]', timeout=5000)
        time.sleep(2)

        # ── ステップ2:「パスワードを使ってログインする」リンクをクリック ──
        try:
            page.click('a:has-text("パスワードを使ってログインする")', timeout=8000)
            time.sleep(2)
        except Exception:
            pass  # すでにパスワード画面なら不要

        # ── ステップ3: パスワード入力 ────────────────────────────
        password_input = page.wait_for_selector(
            'input[type="password"], input[name="__password"]',
            timeout=10000,
        )
        password_input.fill(config.INDEED_PASSWORD)
        time.sleep(3)  # Cloudflare確認の完了を待つ

        # ── ステップ4: ログインボタン ─────────────────────────────
        page.click(
            'button:has-text("ログイン"), button[type="submit"]',
            timeout=5000,
        )

        # ── ログイン完了まで待機 ─────────────────────────────
        try:
            page.wait_for_url("**/employers.indeed.com/**", timeout=25000)
            logger.success("[Indeed] 自動ログイン成功")
            return True
        except PWTimeout:
            logger.warning("[Indeed] ログイン後の画面遷移タイムアウト（Cloudflare等の可能性）")
            return _wait_manual_login(page)

    except Exception as e:
        logger.warning(f"[Indeed] 自動ログインに失敗: {e}")
        return _wait_manual_login(page)

        # ── ステップ1: メールアドレス入力 ──────────────────────
        email_input = page.wait_for_selector(
            'input[type="email"], input[name="__email"], input[id*="email"]',
            timeout=10000,
        )
        email_input.fill(config.INDEED_EMAIL)
        time.sleep(0.5)

        # 「続行」「Continue」ボタンをクリック
        page.click(
            'button[type="submit"], button:has-text("続行"), button:has-text("Continue")',
            timeout=5000,
        )
        time.sleep(3)

        # ── ステップ2: パスワード入力（別ページに遷移） ──────
        try:
            password_input = page.wait_for_selector(
                'input[type="password"], input[name="__password"]',
                timeout=10000,
            )
            password_input.fill(config.INDEED_PASSWORD)
            time.sleep(0.5)
            page.click(
                'button[type="submit"], button:has-text("サインイン"), button:has-text("Sign in")',
                timeout=5000,
            )
        except PWTimeout:
            # パスワード入力欄が出ない = メール認証コードや別の認証方式
            logger.warning("[Indeed] パスワード入力欄が見つかりません（2段階認証かも）")
            return _wait_manual_login(page)

        # ── ログイン完了まで待機 ─────────────────────────────
        try:
            page.wait_for_url("**/employers.indeed.com/**", timeout=20000)
            logger.success("[Indeed] 自動ログイン成功")
            return True
        except PWTimeout:
            logger.warning("[Indeed] ログイン後の画面遷移待機タイムアウト")
            return _wait_manual_login(page)

    except Exception as e:
        logger.warning(f"[Indeed] 自動ログインに失敗: {e}")
        return _wait_manual_login(page)


def _wait_manual_login(page: Page) -> bool:
    """自動ログイン失敗時：ブラウザで手動ログインしてもらう。"""
    print("\n" + "=" * 60)
    print(" 自動ログインに失敗しました。")
    print(" ブラウザの画面でご自身でログインしてください。")
    print(" （CAPTCHA・2段階認証などもブラウザで完了させてください）")
    print(" ")
    print(" ログインが完了したら、ここで Enter キーを押してください ▶")
    print("=" * 60)
    try:
        input()
        logger.info("[Indeed] 手動ログインを受付けました。処理を続行します。")
        return True
    except Exception:
        return False


def _fetch_analytics(page: Page) -> list[JobAnalytics]:
    """アナリティクスページから全求人の指標を取得する。"""
    jobs: list[JobAnalytics] = []
    try:
        page.goto(_ANALYTICS_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # 期間フィルター設定（過去N日）
        try:
            page.click(
                '[data-testid="date-range-selector"], [aria-label*="期間"], button:has-text("期間")',
                timeout=5000,
            )
            time.sleep(0.5)
            days = config.INDEED_ANALYTICS_DAYS
            label = f"過去{days}日" if days in (7, 14, 30) else "過去7日"
            page.click(f'text="{label}"', timeout=3000)
            time.sleep(1)
        except Exception:
            pass

        rows = page.query_selector_all(
            '[data-testid="job-analytics-row"], tr[data-job-id], '
            '.job-analytics-row, table tbody tr'
        )

        for row in rows:
            try:
                title_el = row.query_selector(
                    '[data-testid="job-title"], .job-title, td:first-child a'
                )
                title = title_el.inner_text().strip() if title_el else ""
                if not title:
                    continue

                job_id = row.get_attribute("data-job-id") or ""

                def _num(selector: str) -> int:
                    el = row.query_selector(selector)
                    if not el:
                        return 0
                    txt = el.inner_text().strip().replace(",", "").replace("回", "")
                    return int(txt) if txt.isdigit() else 0

                impressions = _num('[data-testid="impressions"], td:nth-child(2)')
                clicks      = _num('[data-testid="clicks"], td:nth-child(3)')
                applies     = _num('[data-testid="applies"], td:nth-child(4)')

                jobs.append(JobAnalytics(
                    job_id=job_id,
                    title=title,
                    clicks=clicks,
                    applies=applies,
                    impressions=impressions,
                    ctr=clicks / impressions if impressions > 0 else 0.0,
                    conversion=applies / clicks if clicks > 0 else 0.0,
                ))
            except Exception:
                continue

        logger.info(f"[Indeed] アナリティクス取得: {len(jobs)}件")
    except Exception as e:
        logger.error(f"[Indeed] アナリティクス取得失敗: {e}")

    return jobs


def _fetch_job_description(page: Page, job: JobAnalytics) -> str:
    """求人の現在の説明文を取得する。"""
    if not job.job_id:
        return ""
    try:
        page.goto(
            f"https://employers.indeed.com/p/jobs/{job.job_id}/edit",
            wait_until="networkidle",
            timeout=30000,
        )
        time.sleep(1)
        desc_el = page.query_selector(
            '[data-testid="job-description"], textarea[name="jobDescription"], '
            '.ql-editor, [contenteditable="true"]'
        )
        return desc_el.inner_text().strip() if desc_el else ""
    except Exception:
        return ""


def _build_optimized_description(job: JobAnalytics) -> str:
    """アナリティクスに基づき求人説明文を最適化する。"""
    original = job.description
    lines = original.split("\n") if original else []
    improvements: list[str] = []

    # CTRが低い（3%未満）：冒頭キャッチコピーを強化
    if job.ctr < 0.03:
        headline = (lines[0] if lines else job.title)
        improvements.append(f"【注目求人】{headline}｜即日選考可！")

    # 応募転換率が低い（10%未満）：応募ハードルを下げる
    if job.conversion < 0.10 and job.clicks > 0:
        improvements.append("◎ 経験・資格不問でも歓迎！まずはお気軽にご応募ください。")
        improvements.append("◎ WEB応募OK（履歴書は面接時でも可）")

    # クリック数が少ない（50未満）：訴求ワードを追加
    if job.clicks < 50:
        improvements.append("【急募】【未経験OK】【週2日〜勤務可】")

    if not improvements:
        return original

    header = "\n".join(improvements)
    body = original if original else f"「{job.title}」の詳細はIndeedよりご確認ください。"
    return f"{header}\n\n{body}"


def _update_job_description(page: Page, job: JobAnalytics, new_desc: str) -> bool:
    """Indeedの求人編集画面で説明文を更新して保存する。"""
    if not job.job_id:
        return False
    try:
        page.goto(
            f"https://employers.indeed.com/p/jobs/{job.job_id}/edit",
            wait_until="networkidle",
            timeout=30000,
        )
        time.sleep(1)

        desc_el = page.query_selector(
            '[data-testid="job-description"], textarea[name="jobDescription"], '
            '.ql-editor, [contenteditable="true"]'
        )
        if not desc_el:
            logger.warning(f"[Indeed] 説明文フィールドが見つかりません: {job.title}")
            return False

        desc_el.triple_click()
        desc_el.type(new_desc, delay=10)
        time.sleep(0.5)

        save_btn = page.query_selector(
            'button[type="submit"], button:has-text("保存"), button:has-text("更新"), '
            'button:has-text("Save"), button:has-text("Update")'
        )
        if not save_btn:
            logger.warning(f"[Indeed] 保存ボタンが見つかりません: {job.title}")
            return False

        save_btn.click()
        page.wait_for_load_state("networkidle", timeout=10000)
        logger.success(f"[Indeed] 求人更新完了: {job.title}")
        return True
    except Exception as e:
        logger.error(f"[Indeed] 求人更新失敗 '{job.title}': {e}")
        return False


def run_optimization(dry_run: bool = False) -> dict:
    """
    Indeedにログイン → アナリティクス取得 → 求人説明文を自動最適化する。
    dry_run=True の場合は実際の更新をスキップして結果のみ返す。
    """
    if not config.INDEED_EMAIL or not config.INDEED_PASSWORD:
        logger.error("[Indeed] INDEED_EMAIL / INDEED_PASSWORD が未設定です（.envを確認）")
        return {}

    result: dict = {"updated": [], "skipped": [], "analytics": []}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=config.INDEED_HEADLESS)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )
        page = context.new_page()

        try:
            if not _login(page):
                return result

            jobs = _fetch_analytics(page)
            if not jobs:
                logger.warning("[Indeed] 求人データが取得できませんでした")
                return result

            for job in jobs:
                result["analytics"].append({
                    "title": job.title,
                    "impressions": job.impressions,
                    "clicks": job.clicks,
                    "applies": job.applies,
                    "ctr": f"{job.ctr:.2%}",
                    "conversion": f"{job.conversion:.2%}",
                })

                job.description = _fetch_job_description(page, job)
                optimized = _build_optimized_description(job)

                if optimized == job.description:
                    result["skipped"].append(job.title)
                    logger.info(
                        f"[Indeed] 変更不要: {job.title} "
                        f"(CTR={job.ctr:.2%}, CVR={job.conversion:.2%})"
                    )
                    continue

                logger.info(
                    f"[Indeed] 最適化: {job.title} "
                    f"(クリック={job.clicks}, 応募={job.applies}, CTR={job.ctr:.2%})"
                )

                if dry_run:
                    logger.info(f"[DryRun] 更新予定内容:\n{optimized[:300]}...")
                    result["updated"].append(job.title)
                else:
                    if _update_job_description(page, job, optimized):
                        result["updated"].append(job.title)
                    else:
                        result["skipped"].append(job.title)

                time.sleep(config.ACTION_INTERVAL)

        finally:
            context.close()
            browser.close()

    return result
