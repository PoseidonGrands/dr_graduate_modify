import os, requests, csv
import threading
import time

import numpy as np
from datetime import datetime

import pymysql


def init():
    """初始化数据文件"""

    # 检查文件是否存在
    # if not os.path.exists('articleData.csv'):
    #     # 不添加额外的空行
    #     with open('articleData.csv', 'w', encoding='utf-8', newline='') as csvFile:
    #         # 使用csv模块读写csv文件
    #         writer = csv.writer(csvFile)
    #         writer.writerow([
    #             'id',
    #             'likeNum',
    #             'commentsLen',
    #             'reposts_count',    # 转发量
    #             'region',
    #             'content',
    #             'contentLen',
    #             'created_at',
    #             'type',
    #             'detailUrl',
    #             'authorAvatar',
    #             'authorName',
    #             'authorDetail',
    #             'isVip'
    #         ])

    # 覆盖文件
    with open('articleData.csv', 'w', encoding='utf-8', newline='') as csvFile:
        # 使用csv模块读写csv文件
        writer = csv.writer(csvFile)
        writer.writerow([
            'id',
            'likeNum',
            'commentsLen',
            'reposts_count',  # 转发量
            'region',
            'content',
            'contentLen',
            'created_at',
            'type',
            'detailUrl',
            'authorAvatar',
            'authorName',
            'authorDetail',
            'isVip'
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
    conn.commit()
    cursor.close()


def writeRow(row):
    """将数据写入数据文件"""
    with open('articleData.csv', 'a', encoding='utf-8', newline='') as csvFile:
        # 使用csv模块读写csv文件
        writer = csv.writer(csvFile)

        writer.writerow(row)


def parse_json(data, type):
    articles = data['statuses']

    for article in articles:
        id = article['id']
        likeNum = article['attitudes_count']
        commentsLen = article['comments_count']
        reposts_count = article['reposts_count']  # 转发量
        try:
            region = article['region_name'].replace('发布于', '').strip()
        except:
            region = '无'
        content = article['text_raw']
        contentLen = article['textLength']
        created_at = datetime.strptime(article['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
        type = type
        try:
            detailUrl = f'https://weibo.com/{article["id"]}/{article["mblogid"]}'
        except:
            detailUrl = 'null'
        authorAvatar = article['user']['avatar_large']
        authorName = article['user']['screen_name']
        authorDetail = f'https://weibo.com/u/{article["user"]["id"]}'
        isVip = article['user']['v_plus'] # 0或1

        # 存入数据库
        init_db()
        sql = "INSERT IGNORE INTO article_content (articleId, created_at, attitudes_count, region, content, detail_url, screen_name, type, comments_count, reposts_count ) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s); "
        data = (id, created_at, likeNum, region, content, detailUrl, authorName, type, commentsLen, reposts_count)
        # print(article_id)
        save_to_db(sql, data)

        row = [
            id,
            likeNum,
            commentsLen,
            reposts_count,
            region,
            content,
            contentLen,
            created_at,
            type,
            detailUrl,
            authorAvatar,
            authorName,
            authorDetail,
            isVip
        ]

        # 写入文件
        writeRow(row)

    # print(data)


def getNavList():
    """读取全部分类的访问参数"""
    nav_list = []

    # 打开 CSV 文件
    with open('navData.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # 可以选择跳过标题行（如果 CSV 文件有标题行）
        next(reader, None)  # 跳过标题行

        for nav in reader:
            nav_list.append(nav)
        return nav_list


# def getData(url):
#     headers = {
#         'Cookie': 'XSRF-TOKEN=WD2SAKe_HMHSL-eC96RA5db9; login_sid_t=96420783f1229d8df62cd01d8c492d6c; cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=5955062269649.503.1700546055600; SINAGLOBAL=5955062269649.503.1700546055600; ULV=1700546055603:1:1:1:5955062269649.503.1700546055600:; SUB=_2A25IWDYXDeRhGeFG7FQU9yrMwziIHXVrFDffrDV8PUNbmtAGLXfgkW9NeM_WpW37FQwRiAj-iTXomPH-HANVskfi; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpX5KzhUgL.FoMRS0qfS0B71hB2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1hMcSKMXehnX; ALF=1732082118; SSOLoginState=1700546120; WBPSESS=rqOJvTwENBgHefuhw6Dmpw-DhEsc7AzZxVffDnsONVAfSHFrbStfFwWA950eb4j_ecbH-IjlKGqyhGaFj0aJbQk4l-neNJwldk11ta9Xm2EWf3Jp_EyxegXy9wAJbS4Jb46Pppkeu0wHbjSwhRGrDw==',
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
#     }
#
#     # 要获取的行号（从 0 开始计数）
#     row_number = 0  # 获取第 1 行的数据
#
#     # 打开 CSV 文件
#     with open('navData.csv', 'r', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile)
#
#         # 可以选择跳过标题行（如果 CSV 文件有标题行）
#         next(reader, None)  # 跳过标题行
#
#         # 初始化一个变量来保存所需行的数据
#         desired_row = None
#
#         # 遍历文件中的每一行
#         for i, row in enumerate(reader):
#             # 检查当前行号是否是我们要找的行号
#             if i == row_number:
#                 desired_row = row
#                 break  # 找到所需行后退出循环
#
#         print(desired_row[1], desired_row[2])
#
#     params = {
#         'group_id': desired_row[1],
#         'containerid': desired_row[2],
#         'extparam': 'discover|new_feed'
#     }
#
#     resp = requests.get(url, headers=headers, params=params)
#     print(resp.url)
#     print(resp.json())

def getDatas(url, params):
    headers = {
        'Cookie': 'XSRF-TOKEN=WD2SAKe_HMHSL-eC96RA5db9; login_sid_t=96420783f1229d8df62cd01d8c492d6c; cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=5955062269649.503.1700546055600; SINAGLOBAL=5955062269649.503.1700546055600; ULV=1700546055603:1:1:1:5955062269649.503.1700546055600:; SUB=_2A25IWDYXDeRhGeFG7FQU9yrMwziIHXVrFDffrDV8PUNbmtAGLXfgkW9NeM_WpW37FQwRiAj-iTXomPH-HANVskfi; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpX5KzhUgL.FoMRS0qfS0B71hB2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1hMcSKMXehnX; ALF=1732082118; SSOLoginState=1700546120; WBPSESS=rqOJvTwENBgHefuhw6Dmpw-DhEsc7AzZxVffDnsONVAfSHFrbStfFwWA950eb4j_ecbH-IjlKGqyhGaFj0aJbQk4l-neNJwldk11ta9Xm2EWf3Jp_EyxegXy9wAJbS4Jb46Pppkeu0wHbjSwhRGrDw==',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    resp = requests.get(url, headers=headers, params=params)

    # print(resp.url)
    # print(resp.json())

    return resp


if __name__ == '__main__':
    # url = 'https://weibo.com/ajax/feed/hottimeline'

    init()
    nav_list = getNavList()

    # 爬取页数（一页10条数据
    page_num = 10

    # 爬取多少个类型（总共59个类型
    type_count = 59
    # 当前类型索引
    type_index = 0

    MAX_THREADS = 5

    url = 'https://weibo.com/ajax/feed/hottimeline'
    # 爬取数据
    for nav in nav_list:
        # 类型限制
        if type_index >= type_count:
            break

        # 切换类型时休眠1.5s
        time.sleep(1.5)
        # 爬取某种类型下的文章的几页数据
        for page_index in range(1, page_num + 1):
            print(f'正在爬取{nav[0]}分类中的第{page_index}页文章数据')
            time.sleep(1.5)
            params = {
                'group_id': nav[1],
                'containerid': nav[2],
                'extparam': 'discover|new_feed',
                'max_id': page_index
            }
            resp = getDatas(url, params)
            parse_json(resp.json(), nav[0])

        type_index += 1

        print('-----------')




