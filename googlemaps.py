# -*- coding: utf-8 -*-
import itertools
import logging
import re
import time
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

GM_WEBPAGE = 'https://www.google.com/maps/'
MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 40

class GoogleMapsScraper:

    def __init__(self, debug=False):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()

        return True

    def sort_by(self, url, ind):

        self.driver.get(url)
        self.__click_on_cookie_agreement()

        wait = WebDriverWait(self.driver, MAX_WAIT)

        # open dropdown menu
        clicked = False
        tries = 0
        while not clicked and tries < MAX_RETRY:
            try:
                menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
                menu_bt.click()

                clicked = True
                time.sleep(3)
            except Exception as e:
                tries += 1
                self.logger.warn('Failed to click sorting button')

            # failed to open the dropdown
            if tries == MAX_RETRY:
                return -1

        #  element of the list specified according to ind
        recent_rating_bt = self.driver.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[ind]
        recent_rating_bt.click()

        # wait to load review (ajax call)
        time.sleep(5)

        return 0

    def get_places(self, keyword_list=None):

        df_places = pd.DataFrame()
        search_point_url_list = self._gen_search_points_from_square(keyword_list=keyword_list)

        for i, search_point_url in enumerate(search_point_url_list):
            print(search_point_url)

            if (i+1) % 10 == 0:
                print(f"{i}/{len(search_point_url_list)}")
                df_places = df_places[['search_point_url', 'href', 'name', 'rating', 'num_reviews', 'close_time', 'other']]
                df_places.to_csv('output/places_wax.csv', index=False)


            try:
                self.driver.get(search_point_url)
            except NoSuchElementException:
                self.driver.quit()
                self.driver = self.__get_driver()
                self.driver.get(search_point_url)

            # scroll to load all (20) places into the page
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR,
                "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div[aria-label*='Results for']")
            for i in range(10):
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

            # Get places names and href
            time.sleep(2)
            response = BeautifulSoup(self.driver.page_source, 'html.parser')
            div_places = response.select('div[jsaction] > a[href]')

            for div_place in div_places:
                place_info = {
                    'search_point_url': search_point_url.replace('https://www.google.com/maps/search/', ''),
                    'href': div_place['href'],
                    'name': div_place['aria-label']
                }

                df_places = pd.concat([df_places, pd.DataFrame([place_info])], ignore_index=True)

            # TODO: implement click to handle > 20 places

        df_places = df_places[['search_point_url', 'href', 'name']]
        df_places.to_csv('output/places_wax.csv', index=False)



    def get_reviews(self, offset):

        # scroll to load reviews
        self.__scroll()

        # wait for other reviews to load (ajax)
        time.sleep(4)

        # expand review text
        self.__expand_reviews()

        # parse reviews
        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        # TODO: Subject to changes
        rblock = response.find_all('div', class_='jftiEf fontBodyMedium')
        parsed_reviews = []
        for index, review in enumerate(rblock):
            if index >= offset:
                r = self.__parse(review)
                parsed_reviews.append(r)

                # logging to std out
                print(r)

        return parsed_reviews



    # need to use different url wrt reviews one to have all info
    def get_account(self, url):

        self.driver.get(url)
        self.__click_on_cookie_agreement()

        # ajax call also for this section
        time.sleep(2)

        resp = BeautifulSoup(self.driver.page_source, 'html.parser')

        place_data = self.__parse_place(resp, url)

        return place_data


    def __parse(self, review):

        item = {}

        try:
            # TODO: Subject to changes
            id_review = review['data-review-id']
        except Exception as e:
            id_review = None

        try:
            # TODO: Subject to changes
            username = review['aria-label']
        except Exception as e:
            username = None

        try:
            # TODO: Subject to changes
            review_text = self.__filter_string(review.find('span', class_='wiI7pd').text)
        except Exception as e:
            review_text = None

        try:
            # TODO: Subject to changes
            rating = float(review.find('span', class_='kvMYJc')['aria-label'].split(' ')[0])
        except Exception as e:
            rating = None

        try:
            # TODO: Subject to changes
            relative_date = review.find('span', class_='rsqaWe').text
        except Exception as e:
            relative_date = None

        try:
            n_reviews = review.find('div', class_='RfnDt').text.split(' ')[3]
        except Exception as e:
            n_reviews = 0

        try:
            user_url = review.find('button', class_='WEBjve')['data-href']
        except Exception as e:
            user_url = None

        item['id_review'] = id_review
        item['caption'] = review_text

        # depends on language, which depends on geolocation defined by Google Maps
        # custom mapping to transform into date should be implemented
        item['relative_date'] = relative_date

        # store datetime of scraping and apply further processing to calculate
        # correct date as retrieval_date - time(relative_date)
        item['retrieval_date'] = datetime.now()
        item['rating'] = rating
        item['username'] = username
        item['n_review_user'] = n_reviews
        #item['n_photo_user'] = n_photos  ## not available anymore
        item['url_user'] = user_url

        return item


    def __parse_place(self, response, url):

        place = {}

        # 尝试新的标题选择器
        try:
            place['name'] = response.find('h1', class_='DUwDvf lfPIob').text.strip()
        except Exception as e:
            # 如果新选择器失败，尝试旧的选择器
            try:
                place['name'] = response.find('h1', class_='DUwDvf fontHeadlineLarge').text.strip()
            except Exception:
                # 如果都失败，尝试从标题中提取
                try:
                    title_text = response.find('title').text
                    if title_text and 'Google Maps' in title_text:
                        place['name'] = title_text.replace(' - Google Maps', '').strip()
                    else:
                        place['name'] = None
                except Exception:
                    place['name'] = None

        try:
            place['overall_rating'] = float(response.find('div', class_='F7nice ').find('span', class_='ceNzKf')['aria-label'].split(' ')[1])
        except Exception as e:
            place['overall_rating'] = None

        try:
            place['n_reviews'] = int(response.find('div', class_='F7nice ').text.split('(')[1].replace(',', '').replace(')', ''))
        except Exception as e:
            place['n_reviews'] = 0

        try:
            place['n_photos'] = int(response.find('div', class_='YkuOqf').text.replace('.', '').replace(',','').split(' ')[0])
        except Exception as e:
            place['n_photos'] = 0

        try:
            place['category'] = response.find('button', jsaction='pane.rating.category').text.strip()
        except Exception as e:
            # 尝试新的类别选择器
            try:
                category_div = response.find('div', class_='Q5g20')
                if category_div:
                    place['category'] = category_div.text.strip()
                else:
                    place['category'] = None
            except Exception:
                place['category'] = None

        try:
            place['description'] = response.find('div', class_='PYvSYb').text.strip()
        except Exception as e:
            place['description'] = None

        # 尝试从不同的位置获取地址信息
        b_list = response.find_all('div', class_='Io6YTe fontBodyMedium')
        
        # 如果找不到，尝试其他选择器
        if not b_list:
            b_list = response.find_all('div', class_='rogA2c')
            if not b_list:
                b_list = response.find_all('div', {'data-item-id': 'address'})
        
        # 初始化所有字段
        place['address'] = None
        place['website'] = None
        place['phone_number'] = None
        place['plus_code'] = None
        
        # 处理找到的信息元素
        for i, item in enumerate(b_list):
            if item and item.text:
                text = item.text.strip()
                
                # 判断是Plus Code（通常格式为XXXX+XX 城市名）
                if '+' in text and len(text) <= 30 and text.count('+') == 1:
                    # Plus Code通常是数字字母+数字字母的格式
                    parts = text.split('+')
                    if len(parts) == 2 and all(c.isalnum() for c in parts[0][-4:]) and all(c.isalnum() for c in parts[1][:2]):
                        place['plus_code'] = text
                        continue
                
                # 判断是网站（包含http或www或.com等）
                if any(x in text.lower() for x in ['http', 'www.', '.com', '.org', '.net']):
                    place['website'] = text
                # 判断是电话号码（包含数字和电话符号，但排除Plus Code）
                elif any(x in text for x in ['+', '(', ')', '-']) and any(c.isdigit() for c in text) and not ('+' in text and len(text) <= 30):
                    place['phone_number'] = text
                # 否则认为是地址
                else:
                    if not place['address']:  # 只取第一个地址
                        place['address'] = text
        
        # 如果通过上述方式没有获取到地址，尝试从meta标签获取
        if not place['address']:
            try:
                address_meta = response.find('meta', attrs={'itemprop': 'name'})
                if address_meta:
                    address_content = address_meta.get('content', '')
                    # 从完整地址中提取地址部分
                    if '·' in address_content:
                        place['address'] = address_content.split('·')[1].strip()
                    else:
                        place['address'] = address_content
            except Exception:
                pass

        try:
            place['opening_hours'] = response.find('div', class_='t39EBf GUrTXd')['aria-label'].replace('\u202f', ' ')
        except:
            place['opening_hours'] = None

        place['url'] = url

        # 从页面源码meta标签中提取经纬度
        try:
            lat_tag = response.find('meta', itemprop='latitude')
            long_tag = response.find('meta', itemprop='longitude')
            place['lat'] = lat_tag['content'] if lat_tag else None
            place['long'] = long_tag['content'] if long_tag else None
        except Exception:
            place['lat'] = None
            place['long'] = None

        # 如果meta标签中没有经纬度，尝试从JavaScript数据中提取
        if not place['lat'] or not place['long']:
            try:
                import re
                page_text = str(response)
                # 使用正则表达式搜索经纬度模式
                coord_pattern = r'\[3,([0-9.-]+),([0-9.-]+)\]'
                matches = re.findall(coord_pattern, page_text)
                if matches:
                    # 取第一个匹配的坐标对
                    place['long'] = matches[0][0]  # 经度在前
                    place['lat'] = matches[0][1]   # 纬度在后
            except Exception:
                pass

        return place


    def _gen_search_points_from_square(self, keyword_list=None):
        # TODO: Generate search points from corners of square

        keyword_list = [] if keyword_list is None else keyword_list

        square_points = pd.read_csv('input/square_points.csv')

        cities = square_points['city'].unique()

        search_urls = []

        for city in cities:

            df_aux = square_points[square_points['city'] == city]
            latitudes = df_aux['latitude'].unique()
            longitudes = df_aux['longitude'].unique()
            coordinates_list = list(itertools.product(latitudes, longitudes, keyword_list))

            search_urls += [f"https://www.google.com/maps/search/{coordinates[2]}/@{str(coordinates[1])},{str(coordinates[0])},{str(15)}z"
             for coordinates in coordinates_list]

        return search_urls


    # expand review description
    def __expand_reviews(self):
        # use XPath to load complete reviews
        # TODO: Subject to changes
        buttons = self.driver.find_elements(By.CSS_SELECTOR,'button.w8nwRe.kyuRq')
        for button in buttons:
            self.driver.execute_script("arguments[0].click();", button)


    def __scroll(self):
        # TODO: Subject to changes
        scrollable_div = self.driver.find_element(By.CSS_SELECTOR,'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


    def __get_logger(self):
        # create logger
        logger = logging.getLogger('googlemaps-scraper')
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        fh = logging.FileHandler('gm-scraper.log')
        fh.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # add formatter to ch
        fh.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(fh)

        return logger


    def __get_driver(self, debug=False):
        options = Options()

        if not self.debug:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1366,768")

        options.add_argument("--disable-notifications")
        #options.add_argument("--lang=en-GB")
        options.add_argument("--accept-lang=en-GB")
        input_driver = webdriver.Chrome(service=Service(), options=options)

         # click on google agree button so we can continue (not needed anymore)
         # EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "I agree")]')))
        input_driver.get(GM_WEBPAGE)

        return input_driver

    # cookies agreement click
    def __click_on_cookie_agreement(self):
        try:
            agree = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Reject all")]')))
            agree.click()

            # back to the main page
            # self.driver.switch_to_default_content()

            return True
        except:
            return False

    # util function to clean special characters
    def __filter_string(self, str):
        strOut = str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        return strOut
