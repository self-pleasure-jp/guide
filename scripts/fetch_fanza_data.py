name: Fetch FANZA Data

on:
  schedule:
    # 毎日 21:00 UTC = 06:00 JST
    - cron: '0 21 * * *'
  workflow_dispatch:  # 手動実行も可能

jobs:
  fetch-data:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install requests
      
      - name: Fetch FANZA data
        run: |
          python scripts/fetch_fanza_data.py
      
      - name: Commit and push data
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add guide/data/fanza_data.json
          git diff --quiet && git diff --staged --quiet || git commit -m "Update FANZA data - $(date +'%Y-%m-%d %H:%M')"
          git push
