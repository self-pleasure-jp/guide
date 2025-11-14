# FANZA アフィリエイト API 仕様書

## API 認証情報

```
API ID: a2BXCsL2MVUtUeuFBZ1h
アフィリエイトID: yoru365-002
サイト: FANZA
サービス: digital (動画)
フロア: videoa (ビデオ)
```

---

## 1. 商品情報検索API

### 概要
DMM.com、FANZAの商品情報を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/ItemList
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル | 概要 |
|--------|--------|------|--------------|------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h | 登録時に割り振られたID |
| アフィリエイトID | affiliate_id | ○ | yoru365-002 | アフィリエイトID |
| サイト | site | ○ | FANZA | アダルト（FANZA）|
| サービス | service | | digital | サービスコード |
| フロア | floor | | videoa | フロアコード |
| 取得件数 | hits | | 20 | 初期値：20　最大：100 |
| 検索開始位置 | offset | | 1 | 初期値：1　最大：50000 |
| ソート順 | sort | | date | rank/price/-price/date/review/match |
| キーワード | keyword | | | UTF-8で指定 |
| 商品ID | cid | | | content_id |
| 絞りこみ項目 | article | | genre | actress/author/genre/series/maker |
| 絞り込みID | article_id | | 1011199 | 各検索APIから取得可能 |
| 出力形式 | output | | json | json / xml |

### レスポンス例
```json
{
  "result": {
    "status": 200,
    "result_count": 5,
    "total_count": 1450,
    "items": [
      {
        "content_id": "mizd00320",
        "title": "作品タイトル",
        "imageURL": {
          "large": "https://pics.dmm.co.jp/..."
        },
        "prices": {
          "price": "100~"
        },
        "affiliateURL": "https://al.fanza.co.jp/...",
        "date": "2023-03-17 10:00:00",
        "iteminfo": {
          "genre": [
            {"id": 6012, "name": "4時間以上作品"}
          ],
          "actress": [
            {"id": 1054998, "name": "松本いちか"}
          ]
        }
      }
    ]
  }
}
```

---

## 2. フロアAPI

### 概要
フロア一覧を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/FloorList
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル |
|--------|--------|------|--------------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h |
| アフィリエイトID | affiliate_id | ○ | yoru365-002002 |
| 出力形式 | output | | json |

### FANZA 動画フロア
| フロアID | フロア名 | コード |
|----------|----------|--------|
| 43 | ビデオ | videoa |
| 44 | 素人 | videoc |
| 45 | 成人映画 | nikkatsu |
| 46 | アニメ動画 | anime |

---

## 3. ジャンル検索API

### 概要
ジャンル一覧を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/GenreSearch
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル |
|--------|--------|------|--------------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h |
| アフィリエイトID | affiliate_id | ○ | yoru365-002 |
| フロアID | floor_id | ○ | 43 |
| 頭文字(50音) | initial | | あ |
| 取得件数 | hits | | 100 (最大500) |
| 出力形式 | output | | json |

### 人気ジャンル
| ジャンルID | ジャンル名 |
|-----------|-----------|
| 5001 | 中出し |
| 2001 | 巨乳 |
| 1027 | 美少女 |
| 1031 | 痴女 |
| 6012 | 4時間以上作品 |
| 6533 | ハイビジョン |
| 6548 | 独占配信 |

---

## 4. 女優検索API

### 概要
女優情報を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/ActressSearch
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル |
|--------|--------|------|--------------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h |
| アフィリエイトID | affiliate_id | ○ | yoru365-002 |
| 頭文字(50音) | initial | | あ |
| 女優ID | actress_id | | 15365 |
| キーワード | keyword | | あさみ |
| バスト | gte_bust / lte_bust | | 90 |
| ウエスト | gte_waist / lte_waist | | 60 |
| ヒップ | gte_hip / lte_hip | | 90 |
| 取得件数 | hits | | 20 (最大100) |
| ソート順 | sort | | -name |
| 出力形式 | output | | json |

### レスポンス例
```json
{
  "result": {
    "actress": [
      {
        "id": "1054998",
        "name": "松本いちか",
        "ruby": "まつもといちか",
        "bust": "83",
        "cup": "C",
        "waist": "55",
        "hip": "82",
        "imageURL": {
          "large": "http://pics.dmm.co.jp/..."
        },
        "listURL": {
          "digital": "https://al.fanza.co.jp/..."
        }
      }
    ]
  }
}
```

---

## 5. メーカー検索API

### 概要
メーカー一覧を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/MakerSearch
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル |
|--------|--------|------|--------------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h |
| アフィリエイトID | affiliate_id | ○ | yoru365-002 |
| フロアID | floor_id | ○ | 43 |
| 頭文字(50音) | initial | | あ |
| 取得件数 | hits | | 100 (最大500) |
| 出力形式 | output | | json |

### 人気メーカー
| メーカーID | メーカー名 |
|-----------|-----------|
| 1509 | ムーディーズ |
| 1227 | アタッカーズ |
| 5552 | 痴女ヘブン |

---

## 6. シリーズ検索API

### 概要
シリーズ一覧を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/SeriesSearch
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル |
|--------|--------|------|--------------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h |
| アフィリエイトID | affiliate_id | ○ | yoru365-002 |
| フロアID | floor_id | ○ | 43 |
| 頭文字(50音) | initial | | お |
| 取得件数 | hits | | 100 (最大500) |
| 出力形式 | output | | json |

---

## 7. 作者検索API

### 概要
作者一覧を取得するAPI

### リクエストURL
```
https://api.dmm.com/affiliate/v3/AuthorSearch
```

### パラメータ
| 論理名 | 物理名 | 必須 | 値のサンプル |
|--------|--------|------|--------------|
| API ID | api_id | ○ | a2BXCsL2MVUtUeuFBZ1h |
| アフィリエイトID | affiliate_id | ○ | yoru365-002 |
| フロアID | floor_id | ○ | 43 |
| 読み仮名 | initial | | う |
| 取得件数 | hits | | 100 (最大500) |
| 出力形式 | output | | json |

---

## 実装メモ

### CORSプロキシ
ブラウザから直接APIを呼ぶ場合、CORSエラーが発生するため、以下のプロキシを使用：
```javascript
const proxyUrl = 'https://api.allorigins.win/raw?url=';
const response = await fetch(proxyUrl + encodeURIComponent(apiUrl));
```

### 使用例（ジャンルフィルター）
```javascript
// 中出しジャンルで絞り込み
const apiUrl = `https://api.dmm.com/affiliate/v3/ItemList?api_id=${API_ID}&affiliate_id=${AFFILIATE_ID}&site=FANZA&service=digital&floor=videoa&article=genre&article_id=5001&hits=24&output=json`;
```

### 使用例（女優で絞り込み）
```javascript
// 松本いちかの作品で絞り込み
const apiUrl = `https://api.dmm.com/affiliate/v3/ItemList?api_id=${API_ID}&affiliate_id=${AFFILIATE_ID}&site=FANZA&service=digital&floor=videoa&article=actress&article_id=1054998&hits=24&output=json`;
```

---

## 参考リンク

- [FANZA アフィリエイト API ドキュメント](https://affiliate.dmm.com/api/)
- [商品情報API](https://affiliate.dmm.com/api/v3/itemlist.html)
- [フロアAPI](https://affiliate.dmm.com/api/v3/floorlist.html)
