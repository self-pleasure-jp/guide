#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FANZA データ取得スクリプト（修正版）
毎朝実行してデータをJSONファイルに保存
- 人気女優をAPIから動的取得
- デビュー女優の取得ロジック改善
"""

import os
import json
import requests
from datetime import datetime
import time

# FANZA API設定
API_ID = 'a2BXCsL2MVUtUeuFBZ1h'
AFFILIATE_ID = 'yoru365-990'

def fetch_fanza_data(sort='rank', hits=50, genre_id=None, floor='videoa', offset=1):
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
        'offset': offset,
        'output': 'json'
    }
    
    if genre_id:
        params['article'] = 'genre'
        params['article_id'] = genre_id
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Fetching {sort} data (attempt {attempt + 1}/{max_retries})...")
            response = requests.get(base_url, params=params, timeout=60)
            
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

def fetch_popular_actresses(count=5):
    """人気女優をAPIから動的に取得"""
    print(f"\n⭐ Fetching popular actresses (top {count})...")
    
    # 最近の人気作品から女優を抽出
    base_url = 'https://api.dmm.com/affiliate/v3/ItemList'
    
    params = {
        'api_id': API_ID,
        'affiliate_id': AFFILIATE_ID,
        'site': 'FANZA',
        'service': 'digital',
        'floor': 'videoa',
        'sort': 'rank',  # ランキング順
        'hits': 100,      # 多めに取得して女優を抽出
        'output': 'json'
    }
    
    actress_frequency = {}  # 女優名と出現回数
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('result') and data['result'].get('items'):
                items = data['result']['items']
                
                # 女優の出現回数をカウント
                for item in items:
                    if 'iteminfo' in item and 'actress' in item['iteminfo']:
                        for actress in item['iteminfo']['actress']:
                            actress_name = actress.get('name')
                            if actress_name:
                                actress_frequency[actress_name] = actress_frequency.get(actress_name, 0) + 1
                
                # 出現回数でソートして上位を取得
                sorted_actresses = sorted(
                    actress_frequency.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                popular_actresses = [name for name, freq in sorted_actresses[:count]]
                
                print(f"✅ Found {len(popular_actresses)} popular actresses")
                print(f"   Top actresses: {', '.join(popular_actresses)}")
                
                return popular_actresses
    
    except Exception as e:
        print(f"❌ Error fetching popular actresses: {str(e)}")
    
    # フォールバック: 固定リスト
    print("⚠️ Using fallback list")
    fallback_list = [
        '松本いちか',
        '美園和花',
        '沙月恵奈',
        '弥生みづき',
        '逢沢みゆ'
    ]
    return fallback_list[:count]

def fetch_debut_actresses(count=5):
    """デビュー作品から最新新人女優を取得"""
    print(f"\n🆕 Fetching debut actresses (top {count})...")
    
    # ジャンルID: 6006 = デビュー作品
    base_url = 'https://api.dmm.com/affiliate/v3/ItemList'
    
    params = {
        'api_id': API_ID,
        'affiliate_id': AFFILIATE_ID,
        'site': 'FANZA',
        'service': 'digital',
        'floor': 'videoa',
        'article': 'genre',
        'article_id': 6006,  # デビュー作品
        'sort': 'date',      # 新着順
        'hits': 50,          # 多めに取得して女優を抽出
        'output': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('result') and data['result'].get('items'):
                items = data['result']['items']
                
                # 女優名を抽出（重複を除く、新しい順）
                actress_names = []
                seen_actresses = set()
                
                for item in items:
                    if 'iteminfo' in item and 'actress' in item['iteminfo']:
                        for actress in item['iteminfo']['actress']:
                            actress_name = actress.get('name')
                            if actress_name and actress_name not in seen_actresses:
                                actress_names.append(actress_name)
                                seen_actresses.add(actress_name)
                                
                                if len(actress_names) >= count:
                                    break
                    
                    if len(actress_names) >= count:
                        break
                
                print(f"✅ Found {len(actress_names)} debut actresses")
                print(f"   Debut actresses: {', '.join(actress_names)}")
                
                return actress_names[:count]
    
    except Exception as e:
        print(f"❌ Error fetching debut actresses: {str(e)}")
    
    # フォールバック: 空リスト
    print("⚠️ No debut actresses found, using empty list")
    return []

def main():
    print("🚀 Starting FANZA data fetch (Fixed Version)")
    print(f"📅 Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    all_data = {
        'updated_at': datetime.now().isoformat(),
        'rankings': {},
        'floors': {},
        'actresses': {},
        'debut_actresses': {}
    }
    
    # 1. ジャンル別ランキング
    print("\n📊 Fetching genre rankings...")
    print("-" * 60)
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
    print("-" * 60)
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
    
    # 3. 人気女優を取得（APIから動的取得）
    print("\n⭐ Fetching popular actresses (dynamic)...")
    print("-" * 60)
    popular_actresses = fetch_popular_actresses(count=5)
    
    # 4. 人気女優別作品
    print("\n⭐ Fetching popular actress works...")
    print("-" * 60)
    for actress in popular_actresses:
        print(f"\n🔄 Fetching works for {actress}...")
        items = fetch_actress_works(actress, hits=6)
        all_data['actresses'][actress] = items
        time.sleep(1)
    
    # 5. デビュー女優を取得
    print("\n🆕 Fetching debut actresses (dynamic)...")
    print("-" * 60)
    debut_actresses = fetch_debut_actresses(count=5)
    
    # 6. デビュー女優別作品
    if debut_actresses:
        print("\n🆕 Fetching debut actress works...")
        print("-" * 60)
        for actress in debut_actresses:
            print(f"\n🔄 Fetching debut works for {actress}...")
            items = fetch_actress_works(actress, hits=6)
            all_data['debut_actresses'][actress] = items
            time.sleep(1)
    else:
        print("\n⚠️ No debut actresses found, skipping debut works fetch")
    
    # JSONファイルに保存
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f'{output_dir}/fanza_data.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n" + "=" * 60)
    print(f"✅ Data saved to {output_file}")
    
    # 統計情報
    print("\n📊 Summary:")
    print("-" * 60)
    total_items = 0
    for category in ['rankings', 'floors', 'actresses', 'debut_actresses']:
        category_total = 0
        for key, items in all_data[category].items():
            count = len(items)
            category_total += count
            print(f"  {category}/{key}: {count} items")
        total_items += category_total
        if category_total > 0:
            print(f"  └─ {category} total: {category_total} items")
    
    print(f"\n📦 Total items: {total_items}")
    print("=" * 60)
    print("✅ Fetch completed successfully")

if __name__ == '__main__':
    main()
