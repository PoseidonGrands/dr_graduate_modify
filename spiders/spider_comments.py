import os, requests, csv
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from datetime import datetime

import pymysql

from src.features.features import cut_comments_all
from src.models.yuqing import rateComments

# 文章数据链接分析
'''
    https://weibo.com/ajax/statuses/buildComments?
    is_reload=1&
    id=4968751242153172&
    is_show_bulletin=2&
    is_mix=0&
    count=20&
    type=feed&
    uid=5737304133&
    fetch_level=0&
    locale=zh-CN
    
    
    https://weibo.com/ajax/statuses/buildComments?
    flow=0&
    max_id=139559057826101&
    
    flow=0&
    max_id=138871885436798


    其他参数
    refresh=2&
    max_id=1&       第几页
    count=10
'''


global start_time

def init():
    """初始化数据文件"""

    # 检查文件是否存在
    # if not os.path.exists('articleCommentsData.csv'):
    #     # 不添加额外的空行
    #     with open('articleCommentsData.csv', 'w', encoding='utf-8', newline='') as csvFile:
    #         # 使用csv模块读写csv文件
    #         writer = csv.writer(csvFile)
    #
    #         writer.writerow([
    #             'articleId',
    #             'created_at',
    #             'likes_counts',
    #             'region',
    #             'content',
    #             'authorName',
    #             'authorGender',
    #             'authorAddress',
    #             'authorAvatar'
    #         ])

    # 覆盖文件
    with open('articleCommentsData.csv', 'w', encoding='utf-8', newline='') as csvFile:
        # 使用csv模块读写csv文件
        writer = csv.writer(csvFile)

        writer.writerow([
            'articleId',
            'created_at',
            'likes_counts',
            'region',
            'content',
            'authorName',
            'authorGender',
            'authorAddress',
            'authorAvatar'
        ])


def init_db():
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


def writeRow(row):
    """将数据写入数据文件"""
    with open('articleCommentsData.csv', 'a', encoding='utf-8', newline='') as csvFile:
        # 使用csv模块读写csv文件
        writer = csv.writer(csvFile)

        writer.writerow(row)


def getArticleList():
    """读取全部分类的访问参数"""
    article_list = []

    # 打开 CSV 文件
    with open('articleData.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # 可以选择跳过标题行（如果 CSV 文件有标题行）
        next(reader, None)  # 跳过标题行

        for article in reader:
            article_list.append(article)
        return article_list

def get_article_list():
    """读取全部分类的访问参数"""
    article_list = []

    sql = """
        SELECT articleId
        FROM article_content;
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    res = [i[0] for i in res]

    cursor.close()
    return res

def parse_json(data, articleId):
    # 获取全部分类的参数数据
    comments = data['data']
    for comment in comments:
        created_at = datetime.strptime(comment['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
        likes_counts = comment['like_counts']
        try:
            region = comment['source'].replace('来自', '')
        except:
            region = '无'
        content = comment['text_raw']
        authorName = comment['user']['screen_name']
        authorGender = comment['user']['gender']
        authorAddress = comment['user']['location']
        authorAvatar = comment['user']['avatar_large']

        writeRow([
            articleId,
            created_at,
            likes_counts,
            region,
            content,
            authorName,
            authorGender,
            authorAddress,
            authorAvatar
        ])


def getData(url, params):
    """获取一篇文章的评论数据"""

    headers = {
        'Cookie': 'XSRF-TOKEN=WD2SAKe_HMHSL-eC96RA5db9; login_sid_t=96420783f1229d8df62cd01d8c492d6c; cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=5955062269649.503.1700546055600; SINAGLOBAL=5955062269649.503.1700546055600; ULV=1700546055603:1:1:1:5955062269649.503.1700546055600:; SUB=_2A25IWDYXDeRhGeFG7FQU9yrMwziIHXVrFDffrDV8PUNbmtAGLXfgkW9NeM_WpW37FQwRiAj-iTXomPH-HANVskfi; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpX5KzhUgL.FoMRS0qfS0B71hB2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1hMcSKMXehnX; ALF=1732082118; SSOLoginState=1700546120; WBPSESS=rqOJvTwENBgHefuhw6Dmpw-DhEsc7AzZxVffDnsONVAfSHFrbStfFwWA950eb4j_ecbH-IjlKGqyhGaFj0aJbQk4l-neNJwldk11ta9Xm2EWf3Jp_EyxegXy9wAJbS4Jb46Pppkeu0wHbjSwhRGrDw==',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    resp = requests.get(url, headers=headers, params=params)

    # 爬取全部评论数据（翻页，第一页json中的max_id是第二页的请求参数），检查max_id的值是否存在
    # 评论的回复数据：buildComments下的total_number为此评论有几条回复，请求参数的fetch_level为请求的层级，如值为1则爬取每条评论下的1条回复
    # 不实现

    # 爬取一页数据
    if resp.status_code == 200:
        parse_json(resp.json(), params['id'])


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



def crawl_comments(article_id):
    global start_time
    # 爬虫已运行
    # if time.time() - start_time >= 30:
    if time.time() - start_time >= 30:
        start_time = time.time()
        time.sleep(10)
        # time.sleep(2)
        print('爬虫已运行35s,休眠5s...')
        conn.commit()


    print(f"正在爬取文章id为{article_id}的文章评论")
    time.sleep(1)
    params = {
        'id': int(article_id),
        'is_show_bulletin': 2,
        'max_id': 0  # 初始化max_id
    }

    id_list = []
    while True:
        time.sleep(3.3)
        # time.sleep(2.3)
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            data = resp.json()
            max_id = get_comments_data(data, params['id'])

            if max_id == "0" or (max_id in id_list):
                break

            params['max_id'] = max_id
            id_list.append(max_id)
        else:
            print(f"请求失败，状态码：{resp.status_code}")
            break

    print(f"文章id为{article_id}的评论爬取完成")




if __name__ == '__main__':
    #1、从文件读取
    # init()
    #
    # url = 'https://weibo.com/ajax/statuses/buildComments'
    #
    # # 从文章数据文件中读取全部文章
    # article_list = getArticleList()
    #
    # # 爬取全部文章列表里的全部文章
    # for article in article_list:
    #     print(f"正在爬取文章id为{article[0]}的文章评论")
    #     time.sleep(3)
    #     article_id = article[0]
    #     # print(article_id)
    #     params = {
    #         'id': int(article_id),
    #         'is_show_bulletin': 2
    #     }
    #
    #     getData(url, params)

        # break
    # 2、从数据库读取
    init_db()
    headers = {
        'Cookie': 'XSRF-TOKEN=WD2SAKe_HMHSL-eC96RA5db9; login_sid_t=96420783f1229d8df62cd01d8c492d6c; '
                  'cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=5955062269649.503.1700546055600; '
                  'SINAGLOBAL=5955062269649.503.1700546055600; '
                  'ULV=1700546055603:1:1:1:5955062269649.503.1700546055600:; '
                  'SUB=_2A25IWDYXDeRhGeFG7FQU9yrMwziIHXVrFDffrDV8PUNbmtAGLXfgkW9NeM_WpW37FQwRiAj-iTXomPH-HANVskfi; '
                  'SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpX5KzhUgL'
                  '.FoMRS0qfS0B71hB2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1hMcSKMXehnX; ALF=1732082118; '
                  'SSOLoginState=1700546120; '
                  'WBPSESS=rqOJvTwENBgHefuhw6Dmpw-DhEsc7AzZxVffDnsONVAfSHFrbStfFwWA950eb4j_ecbH-IjlKGqyhGaFj0aJbQk4l'
                  '-neNJwldk11ta9Xm2EWf3Jp_EyxegXy9wAJbS4Jb46Pppkeu0wHbjSwhRGrDw==',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.0.0 Safari/537.36 '
    }
    url = 'https://weibo.com/ajax/statuses/buildComments'

    article_list = get_article_list()
    # 1、抓评论
    # # print(article_list)
    #
    # MAX_THREADS = 2
    # start_time = time.time()
    #
    # # 使用ThreadPoolExecutor创建线程池
    # with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    #     # 将爬取评论的任务提交到线程池
    #     future_to_article = {executor.submit(crawl_comments, article_list[index]): article_list[index] for index in
    #                          range(1785, len(article_list))}
    #
    #     # 等待所有任务完成
    #     for future in as_completed(future_to_article):
    #         article_id = future_to_article[future]
    #         try:
    #             data = future.result()
    #         except Exception as exc:
    #             print(f"文章id为{article_id}的评论爬取产生了异常: {exc}")
    #             global conn
    #             conn.commit()
    #
    #
    # # for article in article_list:
    # #     crawl_comments(article)
    #
    # print("所有文章的评论爬取完成")

    # 对全部评论数据分词


    # 2、分词
    sql = """
               SELECT *
               FROM article_comments
           """
    cursor = conn.cursor()
    cursor.execute(sql)
    comments = cursor.fetchall()
    # 获得词频和词云图
    cut_comments_all(comments)

    # # 3、对全部文章的评论数据做情感分析
    # for article_id in article_list:
    #     rateComments(article_id, False)


