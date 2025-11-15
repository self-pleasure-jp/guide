#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動投稿Bot - JSON読み込み版（デビュー女優対応）
data/fanza_data.jsonから作品情報を読み込んで伏字化してXに投稿
"""

import os
import random
import json
from datetime import datetime
import tweepy

# 環境変数から認証情報を取得
API_KEY = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# サイトURL
SITE_URL = 'https://self-pleasure-jp.github.io/guide/'

# 伏字パターン辞書
CENSOR_PATTERNS = {
    '中出し': ['中〇し', '中○し', 'ナ〇出し', 'ナカ〇し'],
    '痴女': ['〇女', '痴〇', 'チ〇女'],
    'セックス': ['セ〇クス', 'セッ〇ス', 'H'],
    '巨乳': ['〇乳', '巨〇', 'キョ〇乳'],
    'フェラ': ['フ〇ラ', 'フェ〇', 'Ф'],
    '騎乗位': ['〇乗位', '騎〇位', 'キジ〇位'],
    '潮吹き': ['〇吹き', '潮〇', 'シオ〇き'],
    '人妻': ['〇妻', '人〇', 'ヒト〇'],
    '熟女': ['〇女', '熟〇', 'ジュク〇'],
    'ハメ撮り': ['ハ〇撮り', 'ハメ〇り', 'ゴニョ〇'],
    '3P': ['3〇', '〇P', 'スリー〇'],
    '4P': ['4〇', '〇P', 'フォー〇'],
    'アナル': ['ア〇ル', 'アナ〇', '〇ナル'],
    'SM': ['S〇', '〇M', 'エス〇'],
    '寝取り': ['寝〇り', '〇取り', 'NTR'],
    '素人': ['〇人', '素〇', 'シロ〇ト'],
    'デビュー': ['デ〇ュー', 'デビ〇ー', '新人'],
    '新人': ['〇人', '新〇', 'ルーキー']
}

def censor_text(text):
    """テキスト内のNGワードを伏字化"""
    censored = text
    for original, patterns in CENSOR_PATTERNS.items():
        if original in censored:
            replacement = random.choice(patterns)
            censored = censored.replace(original, replacement)
    return censored

def load_fanza_data():
    """JSONファイルからFANZAデータを読み込み"""
    try:
        json_path = 'data/fanza_data.json'
        
        print(f"📂 Loading data from {json_path}...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Data loaded successfully!")
        print(f"📅 Updated at: {data.get('updated_at', 'Unknown')}")
        
        return data
        
    except FileNotFoundError:
        print(f"❌ Error: {json_path} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None

def create_ranking_tweet(item):
    """ランキング作品のツイート"""
    if not item or not item.get('title'):
        return None
    
    title = item.get('title', 'タイトル不明')
    censored_title = censor_text(title)
    
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    templates = [
        f"🔥 人気ランキング上位作品\n\n{censored_title}\n\n👉 サンプル動画はこちら\n{SITE_URL}\n\n#FANZA ({time_str})",
        f"✨ 注目の人気作\n\n{censored_title}\n\n今すぐチェック\n{SITE_URL}\n\n({time_str})",
        f"💕 ランキング急上昇\n\n{censored_title}\n\n無料サンプルあり\n{SITE_URL}\n\n({time_str})"
    ]
    
    return random.choice(templates)

def create_actress_tweet(actress_name, item):
    """人気女優作品のツイート"""
    if not item or not item.get('title'):
        return None
    
    title = item.get('title', 'タイトル不明')
    censored_title = censor_text(title)
    censored_actress = censor_text(actress_name)
    
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    templates = [
        f"⭐ 人気AV女優\n\n{censored_actress} 出演作品\n\n{censored_title}\n\nサンプル動画↓\n{SITE_URL}\n\n#FANZA ({time_str})",
        f"💕 {censored_actress}\n\n{censored_title}\n\n今すぐ視聴\n{SITE_URL}\n\n({time_str})",
        f"✨ 注目の女優作品\n\n{censored_actress}\n{censored_title}\n\n詳細はこちら↓\n{SITE_URL}\n\n({time_str})"
    ]
    
    return random.choice(templates)

def create_debut_tweet(actress_name, item):
    """デビュー女優作品のツイート"""
    if not item or not item.get('title'):
        return None
    
    title = item.get('title', 'タイトル不明')
    censored_title = censor_text(title)
    
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    templates = [
        f"🆕 最新新人AV女優\n\n{actress_name}\n\nデ〇ュー作品\n「{censored_title}」\n\nサンプル動画↓\n{SITE_URL}\n\n#FANZA #新人AV女優 ({time_str})",
        f"🌟 注目の新人\n\n{actress_name}\n\n{censored_title}\n\n今すぐチェック\n{SITE_URL}\n\n#新人 ({time_str})",
        f"💫 フレッシュな新人女優\n\n{actress_name}\n{censored_title}\n\n無料サンプルあり↓\n{SITE_URL}\n\n({time_str})"
    ]
    
    return random.choice(templates)

def create_fallback_tweet():
    """フォールバックツイート"""
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    templates = [
        f"🔥 本日の人気作品をチェック\n\n熟〇・人〇・中〇し・巨〇など\n人気ジャンルのランキングを毎日更新中\n\n今すぐ無料で視聴 ({time_str})\n{SITE_URL}",
        f"💕 毎日更新！人気ランキング\n\n中〇し・巨〇・熟〇など\n今日の新着作品をチェック\n\n無料サンプルあり ({time_str})\n{SITE_URL}",
        f"🆕 最新新人AV女優も毎日更新\n\nあなた好みの作品がきっと見つかる\n\n今すぐチェック ({time_str})\n{SITE_URL}"
    ]
    
    return random.choice(templates)

def select_random_content(data):
    """ランダムにコンテンツを選択"""
    content_types = []
    
    # ランキング
    for category, items in data.get('rankings', {}).items():
        if items:
            content_types.append(('ranking', category, items))
    
    # フロア
    for floor, items in data.get('floors', {}).items():
        if items:
            content_types.append(('floor', floor, items))
    
    # 人気女優
    for actress, items in data.get('actresses', {}).items():
        if items:
            content_types.append(('actress', actress, items))
    
    # デビュー女優
    for actress, items in data.get('debut_actresses', {}).items():
        if items:
            content_types.append(('debut', actress, items))
    
    if not content_types:
        return None, None, None
    
    # ランダムに選択
    content_type, name, items = random.choice(content_types)
    item = random.choice(items)
    
    return content_type, name, item

def post_tweet(tweet_text):
    """ツイートを投稿"""
    try:
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        response = client.create_tweet(text=tweet_text)
        return response.data['id']
        
    except Exception as e:
        print(f"❌ Error posting tweet: {str(e)}")
        raise

def main():
    print(f"🚀 Starting FANZA auto-post bot at {datetime.now()}")
    
    # JSONからデータを読み込み
    data = load_fanza_data()
    
    if not data:
        print("⚠️ No data loaded, using fallback tweet")
        tweet_text = create_fallback_tweet()
    else:
        # ランダムにコンテンツを選択
        content_type, name, item = select_random_content(data)
        
        if not item:
            print("⚠️ No items found, using fallback tweet")
            tweet_text = create_fallback_tweet()
        else:
            # コンテンツタイプに応じてツイート作成
            if content_type == 'debut':
                print(f"📝 Creating debut actress tweet for: {name}")
                tweet_text = create_debut_tweet(name, item)
            elif content_type == 'actress':
                print(f"📝 Creating actress tweet for: {name}")
                tweet_text = create_actress_tweet(name, item)
            else:
                print(f"📝 Creating ranking tweet for: {name}")
                tweet_text = create_ranking_tweet(item)
            
            if not tweet_text:
                tweet_text = create_fallback_tweet()
    
    # 280文字制限チェック
    if len(tweet_text) > 280:
        print(f"⚠️ Tweet too long ({len(tweet_text)} chars), using fallback")
        tweet_text = create_fallback_tweet()
    
    # ツイートを投稿
    try:
        tweet_id = post_tweet(tweet_text)
        print(f"✅ Tweet posted successfully")
        print(f"📝 Tweet ID: {tweet_id}")
        print(f"📄 Tweet preview:")
        print(tweet_text)
        print(f"✅ Auto-post completed successfully")
        
    except Exception as e:
        print(f"❌ Failed to post tweet: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()
