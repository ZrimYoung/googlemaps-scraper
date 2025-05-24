# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time

POI_HEADER = [
    'place_name', 'overall_rating', 'n_reviews', 'n_photos', 'category', 'description',
    'address', 'website', 'phone_number', 'plus_code', 'opening_hours', 'lat', 'long'
]
REVIEW_HEADER = [
    'id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'url_user'
]
HEADER = POI_HEADER + REVIEW_HEADER

def csv_writer(outpath):
    targetfile = open('data/' + outpath, mode='w', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(HEADER)
    return writer

ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--o', type=str, default='output.csv', help='output directory')
    parser.add_argument('--sort_by', type=str, default='newest', help='most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.set_defaults(debug=False)

    args = parser.parse_args()

    writer = csv_writer(args.o)

    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:
                url = url.strip()
                # 获取POI元数据
                poi_data = scraper.get_account(url)
                error = scraper.sort_by(url, ind[args.sort_by])
                if error == 0:
                    n = 0
                    while n < args.N:
                        print(colored('[Review ' + str(n) + ']', 'cyan'))
                        reviews = scraper.get_reviews(n)
                        if len(reviews) == 0:
                            break
                        for r in reviews:
                            row_data = [
                                poi_data.get('name'), poi_data.get('overall_rating'), poi_data.get('n_reviews'),
                                poi_data.get('n_photos'), poi_data.get('category'), poi_data.get('description'),
                                poi_data.get('address'), poi_data.get('website'), poi_data.get('phone_number'),
                                poi_data.get('plus_code'), poi_data.get('opening_hours'), poi_data.get('lat'), poi_data.get('long')
                            ]
                            row_data += [
                                r.get('id_review'), r.get('caption'), r.get('relative_date'), r.get('retrieval_date'),
                                r.get('rating'), r.get('username'), r.get('n_review_user'), r.get('url_user')
                            ]
                            writer.writerow(row_data)
                        n += len(reviews)
                else:
                    # 如果没有评论或排序失败，至少输出POI基本信息
                    print(f"无法获取评论，但输出POI基本信息: {poi_data.get('name')}")
                    row_data = [
                        poi_data.get('name'), poi_data.get('overall_rating'), poi_data.get('n_reviews'),
                        poi_data.get('n_photos'), poi_data.get('category'), poi_data.get('description'),
                        poi_data.get('address'), poi_data.get('website'), poi_data.get('phone_number'),
                        poi_data.get('plus_code'), poi_data.get('opening_hours'), poi_data.get('lat'), poi_data.get('long')
                    ]
                    # 添加空的评论字段
                    row_data += [None, None, None, None, None, None, None, None]
                    writer.writerow(row_data)
