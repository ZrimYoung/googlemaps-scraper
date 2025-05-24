# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from bs4 import BeautifulSoup
import time

# 测试URL
test_url = "https://www.google.com/maps?cid=3548426851250613572&hl=en"

print("开始详细调试地点信息抓取...")

with GoogleMapsScraper(debug=True) as scraper:
    print(f"正在访问URL: {test_url}")
    
    # 手动执行get_account的步骤
    scraper.driver.get(test_url)
    
    # 点击cookie同意按钮
    try:
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        agree = WebDriverWait(scraper.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Reject all")]')))
        agree.click()
        print("成功点击拒绝cookies按钮")
    except:
        print("未找到cookies按钮或已处理")
    
    # 增加等待时间
    print("等待页面加载...")
    time.sleep(10)
    
    # 获取页面源码
    page_source = scraper.driver.page_source
    
    # 保存HTML到文件便于分析
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(page_source)
    print("页面源码已保存到 debug_page.html")
    
    # 解析页面
    resp = BeautifulSoup(page_source, 'html.parser')
    
    # 检查一些关键元素
    print("\n=== 调试元素定位 ===")
    
    # 检查标题
    title_element = resp.find('h1', class_='DUwDvf fontHeadlineLarge')
    print(f"标题元素: {title_element}")
    if title_element:
        print(f"标题内容: {title_element.text.strip()}")
    
    # 尝试其他可能的标题选择器
    alternative_titles = [
        resp.find('h1'),
        resp.find('div', {'data-attrid': 'title'}),
        resp.find('span', class_='DUwDvf'),
    ]
    
    print("\n=== 尝试替代标题选择器 ===")
    for i, elem in enumerate(alternative_titles):
        if elem:
            print(f"替代标题 {i}: {elem.text.strip() if elem.text else 'None'}")
    
    # 检查评分元素
    rating_elements = resp.find_all('div', class_='F7nice')
    print(f"\n找到的评分元素数量: {len(rating_elements)}")
    for i, elem in enumerate(rating_elements):
        print(f"评分元素 {i}: {elem}")
    
    # 检查地址等信息元素
    info_elements = resp.find_all('div', class_='Io6YTe fontBodyMedium')
    print(f"\n找到的信息元素数量: {len(info_elements)}")
    for i, elem in enumerate(info_elements[:5]):  # 只显示前5个
        print(f"信息元素 {i}: {elem.text if elem else 'None'}")
    
    # 检查网页标题
    page_title = resp.find('title')
    print(f"\n网页标题: {page_title.text if page_title else 'None'}")
    
    # 检查是否有data-value属性的元素
    data_elements = resp.find_all(attrs={'data-value': True})
    print(f"\n找到的data-value元素数量: {len(data_elements)}")
    
    # 使用get_account方法获取结果
    place_data = scraper.get_account(test_url)
    print(f"\n最终解析结果: {place_data}") 