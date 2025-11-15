#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動ツイート投稿スクリプト（重複防止版）
- カウンターファイルを投稿前に更新
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
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

COUNTER_FILE = 'data/counter.txt'
POSTED_IDS_FILE = 'data/posted_ids.json'
DATA_FILE = 'data/fanza_data.json'
BLUR_RADIUS = 5

def load_fanza_data():
    """JSONデータを読み込み"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Loaded data from {DATA_FILE}")
            return data
    except FileNotFoundError:
        print(f"❌ Error: {DATA_FILE} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None

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

def build_all_items_list(data):
    """全アイテムをフラットなリストに変換"""
    all_items = []
    
    # ランキング
    for category, items in data.get('rankings', {}).items():
        for item in items:
            all_items.append({
                'type': 'ranking',
                'category': category,
                'item': item
            })
    
    # フロア
    for floor, items in data.get('floors', {}).items():
        for item in items:
            all_items.append({
                'type': 'floor',
                'floor': floor,
                'item': item
            })
    
    # 人気女優
    for actress, items in data.get('actresses', {}).items():
        for item in items:
            all_items.append({
                'type': 'actress',
                'name': actress,
                'item': item
            })
    
    # デビュー女優
    for actress, items in data.get('debut_actresses', {}).items():
        for item in items:
            all_items.append({
                'type': 'debut',
                'name': actress,
                'item': item
            })
    
    print(f"📋 Total items: {len(all_items)}")
    return all_items

def select_next_unposted_item(all_items, counter, posted_ids):
    """未投稿のアイテムを選択（カウンターベース）"""
    if not all_items:
        return None, counter
    
    max_attempts = len(all_items)
    for attempt in range(max_attempts):
        index = counter % len(all_items)
        selected = all_items[index]
        content_id = selected['item'].get('content_id')
        
        if content_id and content_id not in posted_ids:
            print(f"🎯 Selected NEW item {index + 1}/{len(all_items)}: {selected['type']} - {content_id}")
            return selected, counter + 1
        else:
            print(f"⏭️  Skipping already posted: {content_id}")
            counter += 1
    
    # 全て投稿済みの場合、リセット
    print("♻️  All items posted, resetting...")
    posted_ids.clear()
    return all_items[0], 1

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

def format_sample_time(item):
    """サンプル動画の時間をフォーマット"""
    sample_url = item.get('sampleMovieURL', {})
    
    if isinstance(sample_url, dict):
        for key, value in sample_url.items():
            if isinstance(value, dict) and 'duration' in value:
                duration = value['duration']
                try:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    return f"({minutes:02d}:{seconds:02d})"
                except:
                    pass
    
    return ""

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

def create_tweet_text(selected):
    """投稿テキストを生成"""
    item_type = selected['type']
    item = selected['item']
    title = censor_text(item.get('title', 'タイトル不明'))
    url = item.get('affiliateURL', item.get('URL', ''))
    
    if len(title) > 70:
        title = title[:67] + '...'
    
    sample_time = format_sample_time(item)
    sample_text = f"無料サンプルあり{sample_time}" if sample_time else "無料サンプルあり"
    
    if item_type == 'debut':
        actress_name = selected['name']
        tweet = f"🆕 新人AV女優デビュー\n\n{actress_name}\n{title}\n\n{sample_text}\n{url}"
    
    elif item_type == 'actress':
        actress_name = selected['name']
        tweet = f"⭐ 人気AV女優\n\n{actress_name}\n{title}\n\n{sample_text}\n{url}"
    
    elif item_type == 'ranking':
        category = selected['category']
        category_map = {
            'creampie': '🔥 中〇しランキング',
            'bigbreasts': '👙 巨〇ランキング',
            'milf': '💋 熟〇ランキング'
        }
        category_name = category_map.get(category, 'ランキング')
        tweet = f"{category_name}\n\n{title}\n\n{sample_text}\n{url}"
    
    elif item_type == 'floor':
        floor = selected['floor']
        floor_map = {
            'amateur': '📺 素人チャンネル',
            'anime': '🎬 アニメ動画'
        }
        floor_name = floor_map.get(floor, 'チャンネル')
        tweet = f"{floor_name}\n\n{title}\n\n{sample_text}\n{url}"
    
    else:
        tweet = f"{title}\n\n{sample_text}\n{url}"
    
    return tweet

def create_fallback_tweet():
    """フォールバックツイート"""
    return """🔥 最新のアダルト動画をチェック！

FANZA（旧DMM）で人気の作品を毎日更新中

無料サンプルあり
https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdigital%2Fvideoa%2F-%2Flist%2F&af_id=yoru365-990&ch=link_tool&ch_id=link"""

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
    print(f"🚀 Starting FANZA auto-post bot (No Duplicate Mode) at {datetime.now()}")
    
    # データ読み込み
    data = load_fanza_data()
    if not data:
        print("⚠️ No data loaded, using fallback tweet")
        tweet_text = create_fallback_tweet()
        post_tweet_with_image(tweet_text, None)
        return
    
    # 投稿済みID読み込み
    posted_ids = load_posted_ids()
    
    # 全アイテムリスト作成
    all_items = build_all_items_list(data)
    if not all_items:
        print("⚠️ No items found, using fallback tweet")
        tweet_text = create_fallback_tweet()
        post_tweet_with_image(tweet_text, None)
        return
    
    # カウンター取得
    counter = get_current_counter()
    
    # 未投稿アイテム選択
    selected, new_counter = select_next_unposted_item(all_items, counter, posted_ids)
    
    if not selected:
        print("⚠️ Could not select item, using fallback tweet")
        tweet_text = create_fallback_tweet()
        post_tweet_with_image(tweet_text, None)
        return
    
    # カウンター更新（投稿前に保存）
    save_counter(new_counter)
    
    # ツイート作成
    tweet_text = create_tweet_text(selected)
    
    # 画像取得とぼかし適用
    item = selected['item']
    content_id = item.get('content_id')
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
        print(f"✅ Post completed! Counter: {counter} → {new_counter}")
    else:
        # 失敗時はカウンターを戻す
        save_counter(counter)
        print(f"⚠️ Tweet failed, counter restored to {counter}")

if __name__ == "__main__":
    main()
