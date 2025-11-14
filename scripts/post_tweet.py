#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動投稿Bot - JSON読み込み版
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
    '凌辱': ['〇辱', '凌〇', 'リョー〇'],
    'レイプ': ['レ〇プ', 'レイ〇', '〇イプ'],
    '強姦': ['〇姦', '強〇', 'ゴー〇'],
    '近親': ['〇親', '近〇', 'キン〇'],
    '素人': ['〇人', '素〇', 'シロ〇ト'],
    'OL': ['〇L', 'O〇', 'オーエ〇'],
    'JK': ['〇K', 'J〇', 'ジェー〇'],
    '女子校生': ['女〇校生', 'J〇', '学〇'],
    '爆乳': ['〇乳', '爆〇', 'バク〇'],
    '美少女': ['美〇女', '〇少女', 'ビショ〇'],
    '美乳': ['〇乳', '美〇', 'ビニュ〇'],
    'パイパン': ['パイ〇', '〇パン', 'ツル〇'],
    'バイブ': ['バ〇ブ', 'バイ〇', '〇イブ'],
    'ぶっかけ': ['ぶっ〇け', '〇っかけ', 'ブッ〇'],
    'フェラチオ': ['フェ〇', 'フ〇チオ', '〇ェラ'],
    'ベロチュー': ['ベロ〇', '〇チュー', 'ベ〇チュー'],
    '放尿': ['〇尿', '放〇', 'ホウ〇'],
    '母乳': ['〇乳', '母〇', 'ボニ〇'],
    'ローター': ['ロー〇', '〇ーター', 'ロ〇タ'],
    '輪姦': ['〇姦', '輪〇', 'リン〇']
}

def censor_text(text):
    """テキスト内のNGワードを伏字化"""
    censored = text
    for original, patterns in CENSOR_PATTERNS.items():
        if original in censored:
            replacement = random.choice(patterns)
            censored = censored.replace(original, replacement)
    return censored

def get_current_post_index():
    """現在の時刻から何番目の投稿かを判定"""
    now = datetime.utcnow()
    hour = now.hour
    minute = now.minute
    
    # UTC時間で判定（JSTから-9時間）
    if hour == 9 and minute >= 0:   # 18:00 JST
        return 0
    elif hour == 10 and minute >= 16:  # 19:16 JST
        return 1
    elif hour == 11 and minute >= 46:  # 20:46 JST
        return 2
    elif hour == 12 and minute >= 36:  # 21:36 JST
        return 3
    elif hour == 13 and minute >= 26:  # 22:26 JST
        return 4
    elif hour == 14 and minute >= 6:  # 23:06 JST
        return 5
    else:
        # 手動実行の場合はランダム
        return random.randint(0, 5)

def load_fanza_data():
    """JSONファイルからFANZAデータを読み込み"""
    try:
        json_path = 'data/fanza_data.json'
        
        print(f"📂 Loading data from {json_path}...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Data loaded successfully!")
        print(f"📅 Updated at: {data.get('updated_at', 'Unknown')}")
        
        # 全ての作品をリストに集める
        all_items = []
        
        # ランキングから
        for category, items in data.get('rankings', {}).items():
            all_items.extend(items)
        
        # フロアから
        for floor, items in data.get('floors', {}).items():
            all_items.extend(items)
        
        # 女優から
        for actress, items in data.get('actresses', {}).items():
            all_items.extend(items)
        
        print(f"📦 Total items loaded: {len(all_items)}")
        
        return all_items
        
    except FileNotFoundError:
        print(f"❌ Error: {json_path} not found!")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return []

def create_tweet_text(item, post_index):
    """ツイート文を作成"""
    if not item or not item.get('title'):
        return create_fallback_tweet()
    
    title = item.get('title', 'タイトル不明')
    censored_title = censor_text(title)
    
    # URLを取得
    affiliate_url = item.get('affiliateURL', SITE_URL)
    
    # 現在時刻を取得
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    # ツイートテンプレート
    templates = [
        f"🔥 新着作品\n\n{censored_title}\n\n👉 詳細はこちら\n{SITE_URL}\n\n#{random.choice(['FANZA', '成人向け', 'アダルト動画'])} ({time_str})",
        f"✨ 本日の注目作\n\n{censored_title}\n\n今すぐチェック ({time_str})\n{SITE_URL}",
        f"💕 人気上昇中\n\n{censored_title}\n\nサンプル動画あり\n{SITE_URL}\n\n({time_str})",
        f"🎬 {censored_title}\n\n詳細・サンプル動画 ({time_str})\n{SITE_URL}",
        f"🌟 話題の作品\n\n{censored_title}\n\n今すぐ視聴 ({time_str})\n{SITE_URL}"
    ]
    
    tweet = random.choice(templates)
    
    # 280文字制限チェック
    if len(tweet) > 280:
        # 長すぎる場合はタイトルを短縮
        max_title_length = 280 - len(tweet) + len(censored_title) - 10
        censored_title = censored_title[:max_title_length] + '...'
        tweet = random.choice(templates)
    
    return tweet

def create_fallback_tweet():
    """フォールバックツイート（データが取得できない場合）"""
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    templates = [
        f"🔥 本日の人気作品をチェック\n\n熟〇・人〇・中〇し・巨〇など\n人気ジャンルのランキングを毎日更新中\n\n今すぐ無料で視聴 ({time_str})\n{SITE_URL}",
        f"💕 毎日更新！人気ランキング\n\n中〇し・巨〇・熟〇など\n今日の新着作品をチェック\n\n無料サンプルあり ({time_str})\n{SITE_URL}",
        f"✨ あなた好みの作品がきっと見つかる\n\n人気ジャンル別ランキング\n毎日更新中！\n\n今すぐチェック ({time_str})\n{SITE_URL}"
    ]
    
    return random.choice(templates)

def post_tweet(tweet_text):
    """ツイートを投稿"""
    try:
        # Twitter API v2 クライアントを作成
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # ツイートを投稿
        response = client.create_tweet(text=tweet_text)
        
        return response.data['id']
        
    except Exception as e:
        print(f"❌ Error posting tweet: {str(e)}")
        raise

def main():
    print(f"🚀 Starting FANZA auto-post bot at {datetime.now()}")
    
    # 投稿するアイテムのインデックスを決定
    post_index = get_current_post_index()
    print(f"📍 Posting item index: {post_index}")
    
    # JSONからデータを読み込み
    items = load_fanza_data()
    
    if not items or len(items) == 0:
        print("⚠️ No items loaded, using fallback tweet")
        tweet_text = create_fallback_tweet()
    elif len(items) <= post_index:
        print(f"⚠️ Not enough items (need {post_index + 1}, got {len(items)}), using random item")
        item = random.choice(items)
        tweet_text = create_tweet_text(item, post_index)
    else:
        # ランダムにアイテムを選択（多様性を確保）
        item = random.choice(items)
        tweet_text = create_tweet_text(item, post_index)
    
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
