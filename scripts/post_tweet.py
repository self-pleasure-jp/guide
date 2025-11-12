#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動投稿Bot - 新着作品対応版
新着作品タイトルを取得して伏字化してXに投稿
"""

import os
import random
import requests
from datetime import datetime
import tweepy

# 環境変数から認証情報を取得
API_KEY = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# FANZA API設定
FANZA_API_ID = os.environ.get('FANZA_API_ID', 'a2BXCsL2MVUtUeuFBZ1h')
FANZA_AFFILIATE_ID = os.environ.get('FANZA_AFFILIATE_ID', 'yoru365-002')

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
    '女子校生': ['〇子校生', '女〇校生', '女子〇生'],
    '学生': ['〇生', '学〇', 'ガク〇'],
    '制服': ['〇服', '制〇', 'セイ〇ク'],
    'パイズリ': ['パ〇ズリ', 'パイ〇リ', '〇イズリ'],
    'クンニ': ['ク〇ニ', 'クン〇', '〇ンニ'],
    '手コキ': ['〇コキ', '手〇キ', 'テ〇キ'],
    '足コキ': ['〇コキ', '足〇キ', 'アシ〇キ'],
    'イキ': ['イ〇', '〇キ'],
    '絶頂': ['〇頂', '絶〇', 'ゼッ〇ウ'],
    '快楽': ['〇楽', '快〇', 'カイ〇ク'],
    '禁欲': ['〇欲', '禁〇', 'キン〇ク'],
    '爆乳': ['〇乳', '爆〇', 'バク〇ュウ'],
    '美少女': ['〇少女', '美〇女', 'ビショ〇ジョ'],
    '美乳': ['〇乳', '美〇', 'ビ〇ュウ'],
    '巨根': ['〇根', '巨〇', 'キョ〇ン'],
    '淫乱': ['〇乱', '淫〇', 'イン〇ン'],
    '痴漢': ['〇漢', '痴〇', 'チ〇ン'],
    '調教': ['〇教', '調〇', 'チョー〇ョウ'],
    '奴隷': ['〇隷', '奴〇', 'ド〇イ']
}

def censor_text(text):
    """テキスト内のNGワードを伏字化"""
    censored = text
    for original, patterns in CENSOR_PATTERNS.items():
        if original in censored:
            # ランダムに伏字パターンを選択
            replacement = random.choice(patterns)
            censored = censored.replace(original, replacement)
    return censored

def get_current_post_index():
    """現在の時刻から何番目の投稿かを判定"""
    now = datetime.utcnow()
    hour = now.hour
    minute = now.minute
    
    # UTC時間で判定（JSTから-9時間）
    if hour == 10 and minute >= 16:  # 19:16 JST
        return 0
    elif hour == 11 and minute >= 46:  # 20:46 JST
        return 1
    elif hour == 12 and minute >= 36:  # 21:36 JST
        return 2
    elif hour == 13 and minute >= 26:  # 22:26 JST
        return 3
    elif hour == 14 and minute >= 6:  # 23:06 JST
        return 4
    else:
        # 手動実行の場合はランダム
        return random.randint(0, 4)

def fetch_latest_video(offset=1):
    """FANZA APIから新着動画を1件だけ取得（高速化）"""
    try:
        # offset: 1=1つ目, 2=2つ目, 3=3つ目...
        api_url = f'https://api.dmm.com/affiliate/v3/ItemList?api_id={FANZA_API_ID}&affiliate_id={FANZA_AFFILIATE_ID}&site=FANZA&service=digital&floor=videoa&sort=date&hits=1&offset={offset}&output=json'
        
        print(f"🔄 Fetching video #{offset} from FANZA API...")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('result') and data['result'].get('items') and len(data['result']['items']) > 0:
            video = data['result']['items'][0]
            print(f"✅ Success! Fetched video: {video.get('title', 'Unknown')[:30]}...")
            return video
        else:
            print("⚠️ No items in response")
            return None
                
    except Exception as e:
        print(f"❌ Error fetching video: {e}")
        return None

def generate_tweet(video, post_index):
    """ツイートを生成"""
    # タイトルを伏字化
    title = video.get('title', '新作動画')
    censored_title = censor_text(title)
    
    # タイトルが長すぎる場合は省略
    if len(censored_title) > 40:
        censored_title = censored_title[:37] + '...'
    
    # ジャンルをランダムに選択して伏字化
    genres = ['中出し', '巨乳', '痴女', '人妻', '熟女', '美少女', '素人']
    selected_genres = random.sample(genres, 3)
    censored_genres = [censor_text(g) for g in selected_genres]
    genres_text = '・'.join(censored_genres)
    
    # 女優名リスト
    actresses = ['松本いちか', '美園和花', '沙月恵奈', '弥生みづき', '逢沢みゆ']
    random_actress = random.choice(actresses)
    
    # 現在時刻（重複防止）
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    # ツイート生成（ハッシュタグなし）
    tweet = f"""🆕 新着作品 #{post_index + 1}
「{censored_title}」

🔥 今日のおすすめジャンル
{genres_text}

👑 注目の女優さん
{random_actress}

🎬 詳しくはこちら ({time_str})
{SITE_URL}"""
    
    return tweet

def post_tweet():
    """Xに投稿"""
    try:
        # 投稿インデックスを判定（0-4）
        post_index = get_current_post_index()
        print(f"📍 Posting video index: {post_index}")
        
        # 必要な1件だけ取得（offset = post_index + 1）
        video = fetch_latest_video(offset=post_index + 1)
        
        if not video:
            print("⚠️ No video available, using fallback tweet")
            # フォールバック用のツイート（ハッシュタグなし + 時刻追加）
            now = datetime.now()
            time_str = now.strftime('%H:%M')
            tweet_text = f"""🔥 本日の人気動画をチェック

熟女・人妻・中〇し・巨〇など
人気ジャンルのランキングを毎日更新中

今すぐ無料で視聴 ({time_str})
{SITE_URL}"""
        else:
            tweet_text = generate_tweet(video, post_index)
        
        # Tweepy v2 Client
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # ツイート投稿
        response = client.create_tweet(text=tweet_text)
        print(f"✅ Tweet posted successfully")
        print(f"📝 Tweet ID: {response.data['id']}")
        print(f"📄 Tweet preview:")
        print(tweet_text)
        
        return True
        
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン処理"""
    print(f"🚀 Starting FANZA auto-post bot at {datetime.now()}")
    
    # 環境変数チェック
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("❌ Missing Twitter API credentials")
        return
    
    # ツイート投稿
    success = post_tweet()
    
    if success:
        print(f"✅ Auto-post completed successfully")
    else:
        print(f"❌ Auto-post failed")

if __name__ == '__main__':
    main()
