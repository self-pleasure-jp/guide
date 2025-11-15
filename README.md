# FANZA 自動投稿システム（1日25件）

## 📊 投稿内訳

| 種類 | 回数 | 説明 |
|------|------|------|
| **商品紹介** | 18回/日 | FANZA新着作品の自動投稿 |
| **サイト誘導** | 5回/日 | guide/ サイトへの誘導投稿 |
| **セルフプレジャー啓発** | 2回/日 | 女性向け啓発投稿 |
| **合計** | **25回/日** | |

---

## 📁 現在のファイル構成

```
guide/
├── .github/
│   └── workflows/
│       ├── auto-post.yml              ★ 置き換え：商品投稿18回/日
│       ├── post-site-promotion.yml    ★ NEW：サイト誘導5回/日
│       ├── post-self-pleasure.yml     ★ NEW：セルフプレジャー2回/日
│       └── fetch-data.yml             既存：そのまま
├── data/
│   ├── .gitkeep                        既存
│   ├── fanza_data.json                 既存
│   ├── fanza_promotion_templates.json  ★ NEW：誘導テンプレート
│   ├── self_pleasure_templates.json    ★ NEW：啓発テンプレート
│   ├── counter.txt                     既存（自動生成）
│   └── posted_ids.json                 既存（自動生成）
├── docs/
│   └── FANZA_API_SPEC.md               既存
├── scripts/
│   ├── fetch_fanza_data.py             既存
│   ├── post_tweet.py                   既存：商品投稿スクリプト
│   ├── post_site_promotion.py          ★ NEW：サイト誘導スクリプト
│   └── post_self_pleasure.py           ★ NEW：セルフプレジャースクリプト
├── README.md                           既存
└── index.html                          既存
```

---

## 🚀 セットアップ手順

### ⚠️ 重要：既存ファイルのバックアップ

```bash
cd guide/

# 既存のauto-post.ymlをバックアップ
cp .github/workflows/auto-post.yml .github/workflows/auto-post.yml.backup
```

### ステップ1：新しいワークフローファイルの配置

```bash
# 1. 商品投稿ワークフロー（既存を上書き）
cp auto-post.yml .github/workflows/

# 2. サイト誘導ワークフロー（新規）
cp post-site-promotion.yml .github/workflows/

# 3. セルフプレジャーワークフロー（新規）
cp post-self-pleasure.yml .github/workflows/
```

### ステップ2：スクリプトファイルの追加

```bash
# scripts/ フォルダに追加
cp post_site_promotion.py scripts/
cp post_self_pleasure.py scripts/
```

### ステップ3：テンプレートファイルの追加

```bash
# data/ フォルダに追加
cp fanza_promotion_templates.json data/
cp self_pleasure_templates.json data/
```

### ステップ4：Git commit & push

```bash
git add .
git commit -m "Add 25 posts/day system (18 products + 5 site promotion + 2 self-pleasure)"
git push
```

---

## ⏰ 投稿スケジュール

### 商品投稿（18回/日）

| 時間帯 | 投稿時刻（JST） | 回数 |
|--------|----------------|------|
| 朝 | 7:00, 8:20, 9:40, 10:30, 11:20, 12:00 | 6回 |
| 昼 | 13:00, 14:10, 15:20, 16:30, 17:00, 17:45 | 6回 |
| 夜 | 18:00, 19:15, 20:30, 21:30, 22:15, 23:00 | 6回 |

### サイト誘導（5回/日）

- 8:00（朝）
- 12:30（昼）
- 16:00（夕方）
- 19:45（夜）
- 22:45（深夜）

### セルフプレジャー啓発（2回/日）

- 14:00（昼）
- 21:00（夜）

---

## 📝 投稿テンプレート例

### 商品投稿（既存システム）
```
🔥新作動画
「熟女の誘惑 麻美ゆま」

人妻・熟女ジャンル
ハイビジョン高画質
[画像]

[FANZA アフィリエイトリンク]
```

### サイト誘導（NEW）
```
🔞大人の時間を楽しむなら
FANZA独占配信作品が充実
熟女・人妻ジャンルも豊富

👉 今すぐチェック
https://self-pleasure-jp.github.io/guide/
```

### セルフプレジャー啓発（NEW）
```
💕自分を大切にする時間

罪悪感を感じる必要はありません。

セルフプレジャーは、自分自身と向き合う大切な時間です。

リラックス効果・ストレス解消・より良い睡眠に繋がります。

#セルフプレジャー #自分を大切に #セルフケア
```

---

## 🔧 カスタマイズ

### 投稿時刻の変更

`.github/workflows/*.yml` の `cron` 部分を編集：

```yaml
- cron: '0 9 * * *'   # JST 18:00 (UTC 9:00)
```

### テンプレートの追加・変更

`data/fanza_promotion_templates.json` を編集：

```json
{
  "templates": [
    "新しいテンプレートを追加..."
  ],
  "service": ["新しいサービス名..."],
  "genre": ["新しいジャンル..."],
  "cta": ["新しいCTA..."]
}
```

---

## ⚠️ 注意事項

### 1. 既存システムとの互換性
- `post_tweet.py`は変更不要
- `fetch_fanza_data.py`も変更不要
- 新しいワークフローを追加するだけ

### 2. 必須キーワード
- サイト誘導投稿では必ず「FANZA」を含める
- 何のサイトか分からないと効果がない

### 3. GitHub Secrets
以下のSecretsが既に設定されているはずです：
- `FANZA_API_ID`
- `FANZA_AFFILIATE_ID`
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`

### 4. 重複投稿を避ける
- 商品投稿は `data/posted_ids.json` で管理
- サイト誘導はランダム組み合わせで自動的に重複回避

---

## 📈 運用開始後の確認事項

- [ ] 全25回の投稿が正常に実行されているか
- [ ] GitHub Actions の実行履歴を確認
- [ ] Twitter で投稿内容を確認
- [ ] サイトへのアクセス数が増加しているか
- [ ] 重複投稿が発生していないか
- [ ] アナリティクスでエンゲージメント確認

---

## 🆘 トラブルシューティング

### 投稿が実行されない
1. GitHub Actions の実行履歴を確認
2. Secrets が正しく設定されているか確認
3. ワークフローファイルの構文エラーをチェック

### 重複投稿が発生
1. `data/posted_ids.json` の内容を確認
2. カウンターがリセットされていないか確認

### テンプレートが表示されない
1. JSONファイルのフォーマットエラーをチェック
2. UTF-8エンコーディングを確認

---

## 📞 サポート

問題が発生した場合は、GitHub Issues で報告してください。

---

**最終更新**: 2025年11月16日  
**システムバージョン**: 1.0.0
