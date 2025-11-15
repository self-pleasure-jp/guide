#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動ツイート投稿スクリプト（最適化版）
- 必要最小限のAPI呼び出し（hits=20）
- offsetは使わない
- 投稿済みIDを記録して完全に重複を防止
"""

import os
import json
import tweepy
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image, ImageFilter

# 環境変数から認証情報を取得
FANZA_API_ID = os.environ.get('FANZA_API_ID')
FANZA_AFFILIATE_ID = os.environ.get('FANZA_AFFILIATE_ID')
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

COUNTER_FILE = 'data/counter.txt'
POSTED_IDS_FILE = 'data/posted_ids.json'
BLUR_RADIUS = 5

def load_posted_ids():
    """投稿済みIDリストを読み込み"""
    try:
        with open(POSTED_IDS_FILE, 'r', encoding='utf-8') as f:
            posted = json.load(f)
            print(f"✅ Loaded {len(posted)} posted IDs")
            return set(posted)
    except FileNotFoundError:
        print("📝 No posted IDs file, starting fresh")
        return set()
    except json.JSONDecodeError:
        print("⚠️ Invalid posted IDs file, starting fresh")
        return set()

def save_posted_ids(posted_ids):
    """投稿済みIDリストを保存"""
    os.makedirs(os.path.dirname(POSTED_IDS_FILE), exist_ok=True)
    with open(POSTED_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(posted_ids), f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(posted_ids)} posted IDs")

def get_current_counter():
    """現在のカウンターを取得"""
    try:
        with open(COUNTER_FILE, 'r') as f:
            counter = int(f.read().strip())
            print(f"📊 Current counter: {counter}")
            return counter
    except FileNotFoundError:
        print("📊 Counter file not found, starting from 0")
        return 0
    except ValueError:
        print("⚠️ Invalid counter value, resetting to 0")
        return 0

def save_counter(counter):
    """カウンターを保存"""
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(counter))
    print(f"💾 Saved counter: {counter}")

def fetch_fanza_new_releases(hits=20):
    """FANZAの新着作品を取得（最小限）"""
    url = "https://api.dmm.com/affiliate/v3/ItemList"
    params = {
        'api_id': FANZA_API_ID,
        'affiliate_id': FANZA_AFFILIATE_ID,
        'site': 'FANZA',
        'service': 'digital',
        'floor': 'videoa',
        'hits': hits,
        'sort': 'date',  # 新着順
        'output': 'json'
    }
    
    try:
        print(f"🌐 Fetching FANZA data (hits={hits})...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result', {}).get('status') == 200:
            items = data.get('result', {}).get('items', [])
            print(f"✅ Fetched {len(items)} items from API")
            return items
        else:
            print(f"⚠️ API Error: {data}")
            return []
    except Exception as e:
        print(f"❌ API Error: {e}")
        return []

def find_next_unposted_item(posted_ids):
    """未投稿のアイテムを探す"""
    # 新着20件を取得
    items = fetch_fanza_new_releases(hits=20)
    
    if not items:
        print("❌ No items fetched from API")
        return None
    
    # 未投稿のアイテムを探す
    for item in items:
        content_id = item.get('content_id')
        if content_id and content_id not in posted_ids:
            print(f"🎯 Found unposted item: {content_id}")
            return item
    
    # すべて投稿済みの場合、履歴をクリア
    print("♻️  All items posted, clearing history...")
    posted_ids.clear()
    save_posted_ids(posted_ids)
    
    # 最初のアイテムを返す
    return items[0] if items else None

def censor_text(text):
    """NGワードを検閲"""
    ng_words = {
        'セックス': 'Sッ〇ス',
        'sex': 's〇x',
        'SEX': 'S〇X',
        'ザーメン': '〇ーメン',
        'フェラ': 'フ〇ラ',
        'ペニス': 'ペ〇ス',
        'まんこ': 'ま〇こ',
        'ちんこ': 'ち〇こ',
        'オナニー': 'オ〇ニー',
        '手コキ': '手〇キ',
        'パイズリ': 'パイ〇リ',
        '中出し': '中〇し',
        '密着': '密〇',
        '絶倫': '絶〇',
        '痴女': '痴〇',
        '人妻': '人〇',
        '不倫': '不〇',
        '寝取': '寝〇',
        'NTR': 'NT〇'
    }
    
    censored = text
    for word, replacement in ng_words.items():
        censored = censored.replace(word, replacement)
    
    return censored

def download_and_blur_image(image_url):
    """画像をダウンロードしてぼかしを適用"""
    try:
        print(f"🖼️  Downloading image from: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        print(f"✅ Image downloaded: {image.size}")
        
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
        print(f"✅ Applied blur (radius={BLUR_RADIUS})")
        
        output = BytesIO()
        blurred_image.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        return output
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def create_tweet_text(item):
    """投稿テキストを生成"""
    title = censor_text(item.get('title', 'タイトル不明'))
    url = item.get('affiliateURL', '')
    
    if len(title) > 70:
        title = title[:67] + '...'
    
    # ジャンル取得
    genres = item.get('iteminfo', {}).get('genre', [])
    genre_text = ''
    if genres:
        genre_names = [g.get('name', '') for g in genres[:2]]
        genre_text = ' / '.join(genre_names)
    
    # 女優取得
    actresses = item.get('iteminfo', {}).get('actress', [])
    actress_text = ''
    if actresses:
        actress_names = [a.get('name', '') for a in actresses[:2]]
        actress_text = ' / '.join(actress_names)
    
    tweet = f"🔥 新作動画\n{title}\n\n"
    
    if actress_text:
        tweet += f"出演: {actress_text}\n"
    
    if genre_text:
        tweet += f"{genre_text}\n"
    
    tweet += f"\n{url}"
    
    return tweet

def post_tweet_with_image(tweet_text, image_data):
    """画像付きツイートを投稿"""
    try:
        # API v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        
        # 画像をアップロード
        if image_data:
            print("📤 Uploading image...")
            media = api.media_upload(filename="blurred_image.jpg", file=image_data)
            media_id = media.media_id_string
            print(f"✅ Image uploaded: {media_id}")
        else:
            media_id = None
        
        # API v2 for tweet
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # ツイート投稿
        if media_id:
            api.create_media_metadata(media_id, alt_text="アダルトコンテンツ")
            response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=tweet_text)
        
        print(f"✅ Tweet posted successfully! Tweet ID: {response.data['id']}")
        return True
        
    except tweepy.errors.Forbidden as e:
        print(f"❌ Forbidden error: {e}")
        print("⚠️ This might be a duplicate tweet")
        return False
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False

def main():
    print(f"🚀 Starting FANZA auto-post bot (Optimized) at {datetime.now()}")
    
    # 投稿済みID読み込み
    posted_ids = load_posted_ids()
    
    # 未投稿アイテムを検索
    item = find_next_unposted_item(posted_ids)
    
    if not item:
        print("❌ Could not find any item to post")
        return
    
    content_id = item.get('content_id')
    print(f"📦 Selected item: {content_id}")
    
    # ツイート作成
    tweet_text = create_tweet_text(item)
    
    # 画像取得とぼかし適用
    image_url = item.get('imageURL', {}).get('large') or item.get('imageURL', {}).get('small')
    
    image_data = None
    if image_url:
        image_data = download_and_blur_image(image_url)
    else:
        print("⚠️ No image URL found")
    
    print("\n" + "="*50)
    print("📝 Tweet preview:")
    print("="*50)
    print(f"Content ID: {content_id}")
    print(tweet_text)
    if image_data:
        print("\n🖼️  Image: Blurred image attached")
    print("="*50 + "\n")
    
    # 投稿
    success = post_tweet_with_image(tweet_text, image_data)
    
    if success:
        # 投稿済みIDに追加
        posted_ids.add(content_id)
        save_posted_ids(posted_ids)
        print(f"✅ Added {content_id} to posted IDs")
        
        # カウンター更新
        counter = get_current_counter()
        save_counter(counter + 1)
        print(f"✅ Post completed! Counter: {counter} → {counter + 1}")
    else:
        print(f"⚠️ Tweet failed")

if __name__ == "__main__":
    main()
