#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA データ取得スクリプト
毎朝実行してデータをJSONファイルに保存
"""

import os
import json
import requests
from datetime import datetime
import time

# FANZA API設定
API_ID = 'a2BXCsL2MVUtUeuFBZ1h'
AFFILIATE_ID = 'yoru365-990'

def fetch_fanza_data(sort='rank', hits=50, genre_id=None, floor='videoa'):
    """FANZA APIからデータを取得"""
    base_url = 'https://api.dmm.com/affiliate/v3/ItemList'
    
    params = {
        'api_id': API_ID,
        'affiliate_id': AFFILIATE_ID,
        'site': 'FANZA',
        'service': 'digital',
        'floor': floor,
        'sort': sort,
        'hits': hits,
        'output': 'json'
    }
    
    if genre_id:
        params['article'] = 'genre'
        params['article_id'] = genre_id
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Fetching {sort} data (attempt {attempt + 1}/{max_retries})...")
            response = requests.get(base_url, params=params, timeout=600)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') and data['result'].get('items'):
                    print(f"✅ Success! Got {len(data['result']['items'])} items")
                    return data['result']['items']
                else:
                    print(f"⚠️ No items in response")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        if attempt < max_retries - 1:
            time.sleep(2)
    
    return []

def search_actress_id(actress_name):
    """女優IDを検索"""
    base_url = 'https://api.dmm.com/affiliate/v3/ActressSearch'
    
    params = {
        'api_id': API_ID,
        'affiliate_id': AFFILIATE_ID,
        'keyword': actress_name,
        'hits': 1,
        'output': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('result') and data['result'].get('actress'):
                return data['result']['actress'][0]['id']
    except Exception as e:
        print(f"❌ Error searching actress {actress_name}: {str(e)}")
    
    return None

def fetch_actress_works(actress_name, hits=6):
    """女優の作品を取得"""
    actress_id = search_actress_id(actress_name)
    
    if not actress_id:
        print(f"⚠️ Actress not found: {actress_name}")
        return []
    
    base_url = 'https://api.dmm.com/affiliate/v3/ItemList'
    
    params = {
        'api_id': API_ID,
        'affiliate_id': AFFILIATE_ID,
        'site': 'FANZA',
        'service': 'digital',
        'floor': 'videoa',
        'article': 'actress',
        'article_id': actress_id,
        'sort': 'review',
        'hits': hits,
        'output': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('result') and data['result'].get('items'):
                print(f"✅ Got {len(data['result']['items'])} works for {actress_name}")
                return data['result']['items']
    except Exception as e:
        print(f"❌ Error fetching works for {actress_name}: {str(e)}")
    
    return []

def main():
    print("🚀 Starting FANZA data fetch")
    print(f"📅 Time: {datetime.now().isoformat()}")
    
    all_data = {
        'updated_at': datetime.now().isoformat(),
        'rankings': {},
        'floors': {},
        'actresses': {}
    }
    
    # 1. ジャンル別ランキング
    print("\n📊 Fetching genre rankings...")
    genres = {
        'creampie': 5001,
        'bigbreasts': 2001,
        'milf': 1014
    }
    
    for genre_name, genre_id in genres.items():
        print(f"\n🔄 Fetching {genre_name} ranking...")
        items = fetch_fanza_data(sort='rank', hits=10, genre_id=genre_id)
        all_data['rankings'][genre_name] = items
        time.sleep(1)
    
    # 2. フロア別ランキング
    print("\n📺 Fetching floor rankings...")
    floors = {
        'amateur': {'floor': 'videoc', 'sort': 'review'},
        'anime': {'floor': 'anime', 'sort': 'date'}
    }
    
    for floor_name, config in floors.items():
        print(f"\n🔄 Fetching {floor_name}...")
        items = fetch_fanza_data(
            sort=config['sort'],
            hits=10,
            floor=config['floor']
        )
        all_data['floors'][floor_name] = items
        time.sleep(1)
    
    # 3. 女優別作品
    print("\n⭐ Fetching actress works...")
    actresses = [
        '松本いちか',
        '美園和花',
        '沙月恵奈',
        '弥生みづき',
        '逢沢みゆ'
    ]
    
    for actress in actresses:
        print(f"\n🔄 Fetching works for {actress}...")
        items = fetch_actress_works(actress, hits=6)
        all_data['actresses'][actress] = items
        time.sleep(1)
    
    # JSONファイルに保存
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f'{output_dir}/fanza_data.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Data saved to {output_file}")
    
    # 統計情報
    total_items = 0
    for category in ['rankings', 'floors', 'actresses']:
        for key, items in all_data[category].items():
            count = len(items)
            total_items += count
            print(f"  {category}/{key}: {count} items")
    
    print(f"\n📦 Total items: {total_items}")
    print("✅ Fetch completed successfully")

if __name__ == '__main__':
    main()
