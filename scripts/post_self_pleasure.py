import tweepy
import json
import random
import os

# Twitter API認証
client = tweepy.Client(
    consumer_key=os.environ['TWITTER_API_KEY'],
    consumer_secret=os.environ['TWITTER_API_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)

# テンプレート読み込み
with open('data/self_pleasure_templates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ランダムに選択
template = random.choice(data['templates'])
message = random.choice(data['message'])
benefit = random.choice(data['benefit'])

# ツイート作成
tweet = template.format(message=message, benefit=benefit)

# 投稿
try:
    response = client.create_tweet(text=tweet)
    print(f"✅ セルフプレジャー投稿成功: {response.data['id']}")
    print(f"内容: {tweet}")
except Exception as e:
    print(f"❌ 投稿エラー: {e}")
