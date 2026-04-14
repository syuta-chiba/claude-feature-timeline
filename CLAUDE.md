# Claude 新機能タイムライン

Anthropic の AI「Claude」の新機能・モデルリリースを時系列で確認できる非公式タイムラインサイト。

## ファイル構成

```
claude-feature-timeline/
├── index.html                  # メインページ（ビルド不要・単一ファイル）
├── data/
│   └── events.js               # イベントデータ（window.EVENTS_DATA として export）
├── scripts/
│   └── fetch_updates.py        # 自動更新スクリプト（Python + BeautifulSoup）
└── .github/workflows/
    └── update.yml              # GitHub Actions（毎朝 5:00 JST に自動実行）
```

## データについて

- イベントデータは `data/events.js` に集約されている（`index.html` にインラインではない）
- `window.EVENTS_DATA = [...]` の形式で export し、`index.html` が `<script src>` で読み込む
- 各エントリの構造：
  ```js
  {
    date: "2026-04-09",   // YYYY-MM-DD
    cat:  "tool",         // model / api / tool / sdk / console / deprecation / other
    title: "...",         // 日本語タイトル
    desc:  "...",         // 日本語説明
    url:   "https://...", // 公式リンク（必須）
    kw:    "...",         // 検索用キーワード（英語・別表記など）
  }
  ```

## 検索の仕組み

`normalize()` 関数で以下を統一してから全文検索：
- 全角 → 半角変換
- ひらがな → カタカナ変換
- カタカナ長音（ー）除去
- スペース区切りで AND 検索

## 自動更新

- スクレイピング元: `https://platform.claude.com/docs/en/release-notes/overview`
- `<h3>` タグを日付、`<li>` タグをエントリとして解析
- `data/events.js` の最新日付より新しいものだけ追記
- カテゴリはキーワードマッチで自動分類

## 公開情報

- GitHub: https://github.com/syuta-chiba/claude-feature-timeline
- 公開URL: https://syuta-chiba.github.io/claude-feature-timeline/
- ホスティング: GitHub Pages（main ブランチの root）

## 注意事項

- 非公式サイト。Anthropic とは無関係
- Python 実行環境: Windows で `python` コマンドが有効（Microsoft Store 版に注意）
- ローカルで `index.html` を `file://` で開く場合、`data/events.js` の読み込みは問題なし
