#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA自動投稿Bot - 簡易版
固定コンテンツでXに投稿
"""

import os
import random
from datetime import datetime
import tweepy

# 環境変数から認証情報を取得
API_KEY = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# サイトURL
SITE_URL = 'https://self-pleasure-jp.github.io/guide/'

# 投稿テンプレート
TWEET_TEMPLATES = [
    {
        'text': """🔥 本日の人気無料エロ動画をチェック！

熟女・人妻・中出し・巨乳など
人気ジャンルのランキングを毎日更新中

今すぐ無料で視聴👇
{site_url}

#FANZA #無料動画 #アダルト #熟女 #人妻""",
    },
    {
        'text': """💕 今日のおすすめ動画

FANZA人気ランキングTOP10
- 中出し
- 巨乳
- 熟女
- 人妻
- 痴女

無料で今すぐ視聴👇
{site_url}

#FANZA #エロ動画 #無料""",
    },
    {
        'text': """🎬 毎日更新！人気動画ランキング

日本語・英語・スペイン語対応
多言語で楽しめる無料動画サイト

チェックはこちら👇
{site_url}

#FANZA #アダルト動画 #無料視聴""",
    },
    {
        'text': """✨ 本日の注目動画

ジャンル別ランキング
女優別人気作品
最新リリース情報

すべて無料で視聴可能👇
{site_url}

#FANZA #無料エロ動画 #人気ランキング""",
    },
    {
        'text': """🌟 無料動画が見放題

・300以上のジャンル
・人気女優の最新作
・毎日更新のランキング

今すぐアクセス👇
{site_url}

#FANZA #無料動画 #見放題""",
    }
]

def post_tweet():
    """Xに投稿"""
    try:
        # Tweepy v2 Client
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # ランダムにテンプレートを選択
        template = random.choice(TWEET_TEMPLATES)
        tweet_text = template['text'].format(site_url=SITE_URL)
        
        # ツイート投稿
        response = client.create_tweet(text=tweet_text)
        print(f"✅ Tweet posted successfully")
        print(f"📝 Tweet ID: {response.data['id']}")
        print(f"📄 Tweet text: {tweet_text[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False

def main():
    """メイン処理"""
    print(f"🚀 Starting FANZA auto-post bot at {datetime.now()}")
    
    # ツイート投稿
    success = post_tweet()
    
    if success:
        print(f"✅ Auto-post completed successfully")
    else:
        print(f"❌ Auto-post failed")

if __name__ == '__main__':
    main()
