# Claude 新機能タイムライン

Anthropic が提供する AI「Claude」の新機能・モデルリリースを時系列で確認できる非公式タイムラインサイトです。

🌐 **公開URL**: https://syuta-chiba.github.io/claude-feature-timeline/

---

## 概要

Claude の新しいモデルリリースや API 機能の追加、ツールの公開などを、わかりやすいタイムライン形式でまとめています。2023年のClaude 1.0リリースから最新情報まで網羅しています。

### 主な機能

- **時系列タイムライン** — 新しい順に並んだカード形式の一覧
- **カテゴリフィルター** — モデルリリース / API機能 / ツール / SDK / コンソール / 非推奨終了 / その他
- **柔軟な検索** — 日本語・英語・ひらがな・カタカナどれでも検索可能。スペース区切りでAND検索にも対応
- **公式リンク付き** — 各カードから Anthropic 公式ページへ別タブで遷移可能
- **毎朝5時自動更新** — GitHub Actions により毎朝 5:00 JST に最新情報を自動取得

---

## 技術構成

```
claude-feature-timeline/
├── index.html                 # メインページ（HTML / CSS / JavaScript）
├── data/
│   └── events.js              # イベントデータ（GitHub Actions により自動更新）
├── scripts/
│   └── fetch_updates.py       # データ取得スクリプト（Python）
└── .github/workflows/
    └── update.yml             # 自動更新ワークフロー（毎朝5時 JST）
```

| 技術 | 用途 |
|---|---|
| HTML / CSS / JavaScript | フロントエンド（ビルド不要の単一ファイル構成） |
| GitHub Pages | 無料ホスティング |
| GitHub Actions | 毎朝5時の自動データ更新 |
| Python + BeautifulSoup | Anthropicページのスクレイピング |

---

## データソース

以下の Anthropic 公式ページから情報を取得しています。

- [Claude Platform リリースノート](https://platform.claude.com/docs/en/release-notes/overview)
- [Anthropic ニュース](https://www.anthropic.com/news)

> **免責事項**: このサイトは非公式のファンサイトです。Anthropic とは無関係です。情報の正確性は保証しません。最新・正確な情報は上記公式ページをご確認ください。

---

## ローカルで動かす

ビルド不要です。`index.html` をブラウザで直接開くだけで動作します。

```bash
git clone https://github.com/syuta-chiba/claude-feature-timeline.git
cd claude-feature-timeline
# index.html をブラウザで開く
```

---

## 自動更新の仕組み

GitHub Actions の `update.yml` が毎朝 5:00 JST（20:00 UTC）に起動し、以下を実行します。

1. Anthropic 公式リリースノートページをフェッチ
2. `data/events.js` の最新日付より新しいエントリを抽出
3. 自動カテゴリ分類（モデル / API / ツール / SDK / コンソール / 非推奨）
4. 新規エントリがあれば `data/events.js` に追記してコミット・プッシュ

Actions タブの「Run workflow」ボタンから手動実行も可能です。

---

## ライセンス

MIT License — ご自由にご利用・改変ください。
