"""
Claude 新機能タイムライン - 自動更新スクリプト
毎朝 5:00 JST (20:00 UTC) に GitHub Actions から実行される。

処理の流れ:
  1. Anthropic 公式リリースノートをフェッチ
  2. data/events.js の最新日付を取得
  3. それより新しいエントリを抽出・自動カテゴリ分類
  4. 新規エントリがあれば data/events.js に追記
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: requests と beautifulsoup4 をインストールしてください")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)

# ─── 設定 ────────────────────────────────────────────────────────────────────
RELEASE_NOTES_URL = "https://platform.claude.com/docs/en/release-notes/overview"
NEWS_URL          = "https://www.anthropic.com/news"
EVENTS_JS_PATH    = Path(__file__).parent.parent / "data" / "events.js"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ClaudeTimelineBot/1.0; "
        "+https://github.com/syuta-chiba/claude-feature-timeline)"
    )
}

# 月名 → 数字マッピング
MONTH_MAP = {
    "january":1,"february":2,"march":3,"april":4,
    "may":5,"june":6,"july":7,"august":8,
    "september":9,"october":10,"november":11,"december":12,
}

# ─── カテゴリ自動分類 ──────────────────────────────────────────────────────────
MODEL_KEYWORDS       = ["we've launched claude","new claude","claude sonnet","claude opus","claude haiku","claude 3","claude 4","model release"]
DEPRECATION_KEYWORDS = ["deprecated","deprecation","retired","retirement","will be retired","returning an error"]
TOOL_KEYWORDS        = ["tool","computer use","web search","web fetch","code execution","agent skills","mcp","managed agents","advisor tool","ant cli","cowork"]
SDK_KEYWORDS         = ["sdk","python sdk","typescript sdk","java sdk","go sdk","ruby sdk","php sdk","c# sdk"]
CONSOLE_KEYWORDS     = ["console","workspaces","workspace","dashboard","usage page","cost page"]

def categorize(text: str) -> str:
    t = text.lower()
    if any(k in t for k in DEPRECATION_KEYWORDS):
        return "deprecation"
    if any(k in t for k in MODEL_KEYWORDS):
        return "model"
    if any(k in t for k in SDK_KEYWORDS):
        return "sdk"
    if any(k in t for k in CONSOLE_KEYWORDS):
        return "console"
    if any(k in t for k in TOOL_KEYWORDS):
        return "tool"
    return "api"

# ─── events.js のパース ────────────────────────────────────────────────────────
def load_existing_dates() -> set[str]:
    """events.js から既存の date 文字列一覧を返す"""
    content = EVENTS_JS_PATH.read_text(encoding="utf-8")
    return set(re.findall(r'date:"(\d{4}-\d{2}-\d{2})"', content))

def get_latest_date(existing_dates: set[str]) -> date:
    if not existing_dates:
        return date(2026, 1, 1)
    return datetime.strptime(max(existing_dates), "%Y-%m-%d").date()

# ─── リリースノートのパース ────────────────────────────────────────────────────
def parse_date_heading(heading_text: str) -> date | None:
    """
    "April 9, 2026" / "April 9th, 2026" のような文字列を date に変換。
    失敗したら None を返す。
    """
    cleaned = re.sub(r"(st|nd|rd|th)", "", heading_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for fmt in ("%B %d, %Y", "%B %d %Y"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass
    return None

def fetch_release_notes() -> list[dict]:
    """
    リリースノートページを取得し、各エントリを辞書のリストで返す。
    [{ "date": "2026-04-09", "title": "...", "desc": "...", "cat": "..." }, ...]
    """
    print(f"フェッチ中: {RELEASE_NOTES_URL}")
    try:
        resp = requests.get(RELEASE_NOTES_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  WARNING: フェッチ失敗 ({e})")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    entries = []
    current_date = None

    # h3 タグを日付見出しとして扱う
    for tag in soup.find_all(["h3", "li"]):
        if tag.name == "h3":
            parsed = parse_date_heading(tag.get_text())
            current_date = parsed
            continue

        if tag.name == "li" and current_date:
            text = tag.get_text(" ", strip=True)
            if len(text) < 20:
                continue  # 短すぎる行はスキップ
            cat = categorize(text)
            # タイトルは最初の句点/ピリオドまで、または 80 字で切る
            title_match = re.split(r"[。\.、,]", text)
            title = title_match[0].strip()[:80] if title_match else text[:80]
            entries.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "cat":  cat,
                "title": title,
                "desc":  text[:300],
                "url":   RELEASE_NOTES_URL,
                "kw":    "",
            })

    print(f"  取得エントリ数: {len(entries)}")
    return entries

# ─── events.js への追記 ────────────────────────────────────────────────────────
def escape_js_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")

def entry_to_js_line(e: dict) -> str:
    return (
        f'  {{ date:"{e["date"]}", cat:"{e["cat"]}", '
        f'title:"{escape_js_str(e["title"])}", '
        f'desc:"{escape_js_str(e["desc"])}", '
        f'url:"{escape_js_str(e["url"])}", '
        f'kw:"{escape_js_str(e["kw"])}" }},'
    )

def inject_new_entries(new_entries: list[dict]) -> None:
    """events.js の window.EVENTS_DATA = [ の直後に新エントリを挿入"""
    content = EVENTS_JS_PATH.read_text(encoding="utf-8")

    # "Last updated" 行を今日の日付に更新
    today = date.today().strftime("%Y-%m-%d")
    content = re.sub(r"// Last updated: \d{4}-\d{2}-\d{2}", f"// Last updated: {today}", content)

    # 挿入位置: window.EVENTS_DATA = [ の直後
    insert_marker = "window.EVENTS_DATA = ["
    pos = content.find(insert_marker)
    if pos == -1:
        print("ERROR: events.js に window.EVENTS_DATA = [ が見つかりません")
        return

    insert_pos = pos + len(insert_marker)
    new_lines = "\n  // 自動追加: " + today + "\n"
    new_lines += "\n".join(entry_to_js_line(e) for e in new_entries) + "\n"

    content = content[:insert_pos] + new_lines + content[insert_pos:]
    EVENTS_JS_PATH.write_text(content, encoding="utf-8")
    print(f"  {len(new_entries)} 件を events.js に追加しました")

# ─── メイン ───────────────────────────────────────────────────────────────────
def main():
    print("=== Claude タイムライン 自動更新 ===")

    existing_dates = load_existing_dates()
    latest_date    = get_latest_date(existing_dates)
    print(f"既存エントリ数: {len(existing_dates)}  最新日付: {latest_date}")

    fetched = fetch_release_notes()

    new_entries = [
        e for e in fetched
        if e["date"] not in existing_dates
        and datetime.strptime(e["date"], "%Y-%m-%d").date() > latest_date
    ]

    if not new_entries:
        print("新しいエントリはありませんでした。")
        return

    # 新しい順にソート
    new_entries.sort(key=lambda e: e["date"], reverse=True)
    print(f"新規エントリ: {len(new_entries)} 件")
    for e in new_entries:
        print(f"  [{e['date']}] {e['title'][:60]}")

    inject_new_entries(new_entries)
    print("完了!")

if __name__ == "__main__":
    main()
