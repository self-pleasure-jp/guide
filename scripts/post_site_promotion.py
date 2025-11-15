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
with open('data/fanza_promotion_templates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ランダムに選択
template = random.choice(data['templates'])
service = random.choice(data['service'])
genre = random.choice(data['genre'])
cta = random.choice(data['cta'])

# ツイート作成
tweet = template.format(service=service, genre=genre, cta=cta)

# 投稿
try:
    response = client.create_tweet(text=tweet)
    print(f"✅ サイト誘導投稿成功: {response.data['id']}")
    print(f"内容: {tweet}")
except Exception as e:
    print(f"❌ 投稿エラー: {e}")
