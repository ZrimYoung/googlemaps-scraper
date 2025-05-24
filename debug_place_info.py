# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
import json

# 测试URL
test_url = "https://www.google.com/maps?cid=3548426851250613572&hl=en"

print("开始测试地点信息抓取...")

with GoogleMapsScraper(debug=True) as scraper:
    print(f"正在访问URL: {test_url}")
    
    # 获取POI元数据
    poi_data = scraper.get_account(test_url)
    
    print("获取到的地点信息:")
    print(json.dumps(poi_data, indent=2, ensure_ascii=False))
    
    # 检查每个字段
    print("\n字段检查:")
    fields = ['name', 'overall_rating', 'n_reviews', 'n_photos', 'category', 
              'description', 'address', 'website', 'phone_number', 'plus_code', 
              'opening_hours', 'lat', 'long']
    
    for field in fields:
        value = poi_data.get(field)
        print(f"{field}: {value} (类型: {type(value)})") 