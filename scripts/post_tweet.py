#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動ツイート投稿スクリプト（順番投稿方式 v2）
- ランキング名明記
- 個別リンク
- サンプル動画時間表示（リンクの上）
"""

import os
import json
import tweepy
from datetime import datetime
import re

# 環境変数から認証情報を取得
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

COUNTER_FILE = 'data/counter.txt'
DATA_FILE = 'data/fanza_data.json'

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
    
    # デビュー女優（Twitterには投稿するが、index.htmlには表示しない）
    for actress, items in data.get('debut_actresses', {}).items():
        for item in items:
            all_items.append({
                'type': 'debut',
                'name': actress,
                'item': item
            })
    
    print(f"📋 Total items: {len(all_items)}")
    return all_items

def select_item_by_counter(all_items, counter):
    """カウンターに基づいてアイテムを選択"""
    if not all_items:
        return None
    
    # ループさせる（全部投稿したら最初に戻る）
    index = counter % len(all_items)
    selected = all_items[index]
    
    print(f"🎯 Selected item {index + 1}/{len(all_items)}: {selected['type']}")
    return selected

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
        'パイズリ': 'パイ〇リ'
    }
    
    censored = text
    for word, replacement in ng_words.items():
        censored = censored.replace(word, replacement)
    
    return censored

def format_sample_time(item):
    """サンプル動画の時間をフォーマット"""
    # sampleMovieURLがあれば時間情報を取得
    sample_url = item.get('sampleMovieURL', {})
    
    if isinstance(sample_url, dict):
        # size_476_306 などのキーから時間を取得
        for key, value in sample_url.items():
            if isinstance(value, dict) and 'duration' in value:
                duration = value['duration']
                # MM:SS形式に変換
                try:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    return f"({minutes:02d}:{seconds:02d})"
                except:
                    pass
    
    return ""

def create_tweet_text(selected):
    """投稿テキストを生成"""
    item_type = selected['type']
    item = selected['item']
    title = censor_text(item.get('title', 'タイトル不明'))
    url = item.get('affiliateURL', item.get('URL', ''))
    
    # タイトルを70文字に制限
    if len(title) > 70:
        title = title[:67] + '...'
    
    # サンプル動画時間を取得
    sample_time = format_sample_time(item)
    sample_text = f"無料サンプルあり{sample_time}" if sample_time else "無料サンプルあり"
    
    if item_type == 'debut':
        actress_name = selected['name']
        tweet = f"🆕 新人AV女優デビュー\n\n{actress_name}\n{title}\n\n{sample_text}\n{url}\n\n#FANZA"
    
    elif item_type == 'actress':
        actress_name = selected['name']
        tweet = f"⭐ 人気AV女優\n\n{actress_name}\n{title}\n\n{sample_text}\n{url}\n\n#FANZA"
    
    elif item_type == 'ranking':
        category = selected['category']
        category_map = {
            'creampie': '🔥 中出しランキング',
            'bigbreasts': '👙 巨乳ランキング',
            'milf': '💋 熟女ランキング'
        }
        category_name = category_map.get(category, 'ランキング')
        tweet = f"{category_name}\n\n{title}\n\n{sample_text}\n{url}\n\n#FANZA"
    
    elif item_type == 'floor':
        floor = selected['floor']
        floor_map = {
            'amateur': '📺 素人チャンネル',
            'anime': '🎬 アニメ動画'
        }
        floor_name = floor_map.get(floor, 'チャンネル')
        tweet = f"{floor_name}\n\n{title}\n\n{sample_text}\n{url}\n\n#FANZA"
    
    else:
        tweet = f"{title}\n\n{sample_text}\n{url}\n\n#FANZA"
    
    return tweet

def create_fallback_tweet():
    """フォールバックツイート"""
    return """🔥 最新のアダルト動画をチェック！

FANZA（旧DMM）で人気の作品を毎日更新中

無料サンプルあり
https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdigital%2Fvideoa%2F-%2Flist%2F&af_id=yoru365-990&ch=link_tool&ch_id=link"""

def post_tweet(tweet_text):
    """ツイートを投稿"""
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        
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
    print(f"🚀 Starting FANZA auto-post bot (Sequential Mode v2) at {datetime.now()}")
    
    # データ読み込み
    data = load_fanza_data()
    if not data:
        print("⚠️ No data loaded, using fallback tweet")
        tweet_text = create_fallback_tweet()
        post_tweet(tweet_text)
        return
    
    # 全アイテムリスト作成
    all_items = build_all_items_list(data)
    if not all_items:
        print("⚠️ No items found, using fallback tweet")
        tweet_text = create_fallback_tweet()
        post_tweet(tweet_text)
        return
    
    # カウンター取得
    counter = get_current_counter()
    
    # アイテム選択
    selected = select_item_by_counter(all_items, counter)
    if not selected:
        print("⚠️ Could not select item, using fallback tweet")
        tweet_text = create_fallback_tweet()
        post_tweet(tweet_text)
        return
    
    # ツイート作成
    tweet_text = create_tweet_text(selected)
    
    print("\n" + "="*50)
    print("📝 Tweet preview:")
    print("="*50)
    print(tweet_text)
    print("="*50 + "\n")
    
    # 投稿
    success = post_tweet(tweet_text)
    
    if success:
        # カウンターを進める
        new_counter = counter + 1
        save_counter(new_counter)
        print(f"✅ Counter updated: {counter} → {new_counter}")
    else:
        print("⚠️ Tweet failed, counter not updated")

if __name__ == "__main__":
    main()
