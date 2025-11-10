#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動投稿Bot
FANZA APIから人気動画を取得してXに投稿
"""

import os
import requests
import random
from datetime import datetime
import tweepy

# 環境変数から認証情報を取得
API_KEY = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# FANZA API認証情報
FANZA_API_ID = 'a2BXCsL2MVUtUeuFBZ1h'
FANZA_AFFILIATE_ID = 'yoru365-990'

# サイトURL
SITE_URL = 'https://self-pleasure-jp.github.io/guide/'

def get_fanza_videos():
    """FANZA APIから人気動画を取得"""
    # 人気ジャンル
    genres = [
        {'id': 5001, 'name': '中出し'},
        {'id': 2001, 'name': '巨乳'},
        {'id': 1014, 'name': '熟女'},
        {'id': 1039, 'name': '人妻'},
        {'id': 1031, 'name': '痴女'}
    ]
    
    # ランダムにジャンルを選択
    genre = random.choice(genres)
    
    # CORS回避用プロキシ
    proxy_url = 'https://api.allorigins.win/raw?url='
    
    # FANZA API URL
    api_url = f"https://api.dmm.com/affiliate/v3/ItemList?api_id={FANZA_API_ID}&affiliate_id={FANZA_AFFILIATE_ID}&site=FANZA&service=digital&floor=videoa&article=genre&article_id={genre['id']}&sort=rank&hits=10&output=json"
    
    try:
        response = requests.get(proxy_url + requests.utils.quote(api_url), timeout=30)
        data = response.json()
        
        if data.get('result') and data['result'].get('items'):
            items = data['result']['items']
            # プレースホルダー画像を除外
            valid_items = [item for item in items if item.get('imageURL', {}).get('large')]
            
            if valid_items:
                video = valid_items[0]  # 1位の動画を取得
                return {
                    'title': video.get('title', ''),
                    'url': video.get('affiliateURL', ''),
                    'image_url': video['imageURL'].get('large', ''),
                    'genre': genre['name']
                }
    except Exception as e:
        print(f"Error fetching FANZA data: {e}")
    
    return None

def download_image(image_url):
    """画像をダウンロード"""
    try:
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            with open('/tmp/thumbnail.jpg', 'wb') as f:
                f.write(response.content)
            return '/tmp/thumbnail.jpg'
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def post_tweet(video_data):
    """Xに投稿"""
    try:
        # Tweepy v2 Client
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        
        # ツイート文を作成
        tweet_text = f"""🔥 {video_data['genre']}ランキング1位

{video_data['title'][:50]}...

今すぐチェック👇
{SITE_URL}

#FANZA #無料動画 #{video_data['genre']}"""
        
        # 画像をダウンロード
        image_path = download_image(video_data['image_url'])
        
        if image_path:
            # 画像付きでツイート
            media = api.media_upload(image_path)
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            print(f"✅ Tweet posted successfully with image")
        else:
            # テキストのみでツイート
            client.create_tweet(text=tweet_text)
            print(f"✅ Tweet posted successfully (text only)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False

def main():
    """メイン処理"""
    print(f"🚀 Starting FANZA auto-post bot at {datetime.now()}")
    
    # 動画データを取得
    video_data = get_fanza_videos()
    
    if video_data:
        print(f"📹 Video found: {video_data['title'][:50]}...")
        
        # ツイート投稿
        success = post_tweet(video_data)
        
        if success:
            print(f"✅ Auto-post completed successfully")
        else:
            print(f"❌ Auto-post failed")
    else:
        print(f"❌ No video data available")

if __name__ == '__main__':
    main()
