import os, requests, csv
import time
import pymysql

import numpy as np
from datetime import datetime


def init():
    """数据库配置初始化"""
    global conn
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='2280139492',
        database='dr_weibo',
        charset='utf8mb4'
    )


def save_to_db(query, data):
    cursor = conn.cursor()
    cursor.execute(query, data)
    conn.commit()
    cursor.close()


def get_comments_data(data, article_id):
    comments = data['data']
    max_id = str(data['max_id'])
    for comment in comments:
        comment_id = comment['id']
        article_id = article_id
        content = comment['text_raw']
        like_counts = comment['like_counts']
        # print(content)
        try:
            region = comment['source'].replace('来自', '')
        except:
            region = '无'
        created_at = datetime.strptime(comment['created_at'], '%a %b %d %H:%M:%S %z %Y')
        screen_name = comment['user']['screen_name']
        authorGender = comment['user']['gender']

        # 保存到数据库
        insert_data_query = "INSERT IGNORE INTO article_comments (commentId, articleId, content, likeCounts, region, created_at, " \
                            "screen_name, commenterGender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); "
        data = (comment_id, article_id, content, like_counts, region, created_at, screen_name, authorGender)
        # print(article_id)
        save_to_db(insert_data_query, data)
    return max_id


def spider_article(headers, url, params):
    resp = requests.get(url, headers=headers, params=params)
    # 数据获取成功，解析数据
    if resp.status_code == 200:
        data = resp.json()
        print("data is:", data)
        articleId = data['id']
        created_at = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
        attitudes_count = data['attitudes_count']
        try:
            region = data['region_name'].replace('发布于', '').strip()
        except:
            region = '无'
        content = data['text']
        try:
            detailUrl = f'https://weibo.com/{data["id"]}/{data["mblogid"]}'
        except:
            detailUrl = 'null'
        screen_name = data['user']['screen_name']

        commentsLen = data['comments_count']
        reposts_count = data['reposts_count']  # 转发量
        type = '无'

        # 保存到数据库
        insert_data_query = "INSERT IGNORE INTO article_content (articleId, created_at, attitudes_count, region, content, detail_url, screen_name, type, comments_count, reposts_count) " \
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = (articleId, created_at, attitudes_count, region, content, detailUrl, screen_name, type, commentsLen, reposts_count)
        save_to_db(insert_data_query, (data))

        return articleId


def spider_comments(headers, url, params):
    """只爬取评论，不爬取回复"""
    # 先爬取第一页评论，获取到max_id
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        max_id = get_comments_data(data, params['id'])
        # print(f"max_id is {max_id}")

        # 爬取下一页，知道爬取的页面数据里max_id为0，代表是最后一页数据
        id_list = []
        while True:
            time.sleep(1)
            # print('爬取中...')
            params['max_id'] = max_id

            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                max_id = get_comments_data(data, params['id'])

                print(max_id)
                if max_id == "0" or (max_id in id_list):
                    break

                id_list.append(max_id)

def spider(url):
    print('爬取微博：' + url)
    init()

    # 取出文章内容的请求id
    start = url.rfind('/')
    end = url.rfind('?')
    weibo_id = url[start + 1:end]
    print(weibo_id)

    headers = {
        'Cookie': 'XSRF-TOKEN=Hf6ybqxmOhkajTWPaeoZpbKd; SUB=_2A25LEbmoDeRhGeFG7FQU9yrMwziIHXVobrNgrDV8PUNbmtAGLVLlkW9NeM_WpSnvZBDF497p9_SPK2qkbLDKxF4K; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpX5KzhUgL.FoMRS0qfS0B71hB2dJLoI7yE9gpDqfvRw5tt; ALF=02_1715295993; WBPSESS=rqOJvTwENBgHefuhw6Dmpw-DhEsc7AzZxVffDnsONVCxBqb-ON-yioO62vDsqFxoapLUeAgx6hgxo9VjrrX6Gwgq7iTHaRFqiPYFyjWSOuaYcVwehotHw84BkB-ygPU_35M0wQFei3vCrXXxNBbkaA==',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.0.0 Safari/537.36 '
    }

    # 文章内容的请求url
    url_article = 'https://weibo.com/ajax/statuses/show'
    # 文章评论的请求url（多条
    url_comments = 'https://weibo.com/ajax/statuses/buildComments'

    article_params = {
        'id': weibo_id,
        'locale': 'zh-CN'
    }

    # 爬取文章内容
    try:
        article_id = spider_article(headers, url_article, article_params)

        comments_params = {
            'id': article_id,
            'is_show_bulletin': 2
        }
        # 爬取文章评论
        spider_comments(headers, url_comments, comments_params)
    finally:
        conn.close()

    return article_id

