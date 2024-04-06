import random
import urllib.parse

import requests
import time
import pymysql

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

t = ThreadPoolExecutor(10)
max_id_queue = Queue(maxsize=10)
article_id = None
proxies = []


class ProxyException(Exception):
    def __init__(self, message):
        self.message = message


def connect_to_db():
    """数据库配置初始化"""
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='2280139492',
        database='dr_weibo',
        charset='utf8mb4'
    )
    return conn


conn = connect_to_db()


def save_to_db(query, data):
    global conn
    if conn is None:
        connect_to_db()
    cursor = conn.cursor()

    cursor.execute(query, data)
    conn.commit()
    cursor.close()


def spider_article(headers, url, params):
    """将文章内容解析并入库，取出文章id用于请求评论数据"""
    resp = requests.get(url, headers=headers, params=params)
    # 数据获取成功，解析数据
    if resp.status_code == 200:
        data = resp.json()
        print("data is:", data)
        articleId = data['id']
        global article_id
        article_id = articleId
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
        data = (articleId, created_at, attitudes_count, region, content, detailUrl, screen_name, type, commentsLen,
                reposts_count)
        save_to_db(insert_data_query, (data))

        return articleId


def get_comments_data(data, article_id):
    """解析一页评论数据"""
    comments = data['data']
    max_id = str(data['max_id'])
    if max_id != '0':
        max_id_queue.put(max_id)
    # 解析每条评论数据
    print(f'评论数据有:{len(comments)}')
    for comment in comments:
        comment_id = comment['id']
        # article_id = article_id
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


def get_public_ip():
    """获取公网ip"""
    try:
        response = requests.get('http://myip.ipip.net/json')
        if response.status_code == 200:
            data = response.json()
            if data['ret'] == 'ok':
                return data['data']['ip']
    except Exception as e:
        print("获取公网IP地址时出错:", e)
        return None
    # try:
    #     response = requests.get('https://api.ipify.org?format=json')
    #     if response.status_code == 200:
    #         data = response.json()
    #         return data.get('ip')
    #     else:
    #
    #         return None
    #
    # except Exception as e:
    #     print("再次尝试获取...")
    #     response = requests.get('https://httpbin.org/ip')
    #     if response.status_code == 200:
    #         data = response.json()
    #         return data.get('origin')
    #     else:
    #         print("无法获取公网IP地址：", response.status_code)
    #         return None


def get_proxy():
    """获取静态代理IP"""
    proxy = requests.get('')
    res = proxy.json()['data']
    # print(res)
    global proxies
    for i in res:
        # print(i)
        proxies.append(f'{i["ip"]}:{i["port"]}')
    print(proxies)


def get_random_id():
    proxy = random.choice(proxies)
    return {'http': proxy, 'https': proxy}


def reset_white_list():
    # 代理申请白名单处理
    # 蜻蜓代理白名单处理
    current_ip = get_public_ip()
    print(current_ip)
    url = 'https://proxyapi.horocn.com/api/ip/whitelist'
    params = {
        'token': '1cecb7591461c8187d39b262f39dad0e',
        'ip': current_ip
    }
    res_del = requests.delete(url, params=params)
    res_put = requests.put(url, params=params)
    print(res_del.text)
    print(res_put.text)



def spider_comments(headers, url):
    """只爬取评论，不爬取回复"""
    comments_params = {
        'id': '-1',
        'is_show_bulletin': 2,
        'max_id': 0
    }

    # 存储id，确保不出现重复id
    id_list = []

    # 优先用本机公网地址访问（如果爬取到某个max_id的data长度为0，切换代理ip爬取

    # 代理获取成功，用代理爬取
    if len(proxies) != 0:
        while 1:
            # article_id为空则不获取评论数据
            if article_id is None:
                continue

            comments_params['id'] = article_id

            resp = None
            for _ in range(0, len(proxies)):
                proxy = get_random_id()
                try:
                    print(f'使用代理:{proxy}')
                    resp = requests.get(url, headers=headers, params=comments_params, proxies=proxy, timeout=2)
                    # 该ip请求成功了无需再次请求
                    break
                except Exception as e:
                    print(e)
                    continue

            if resp is not None and resp.status_code == 200:
                data = resp.json()
                # 用一个线程处理每页的数据解析
                t.submit(get_comments_data, data, article_id)

                try:
                    # 循环爬取下一页，直到爬取的页面数据里max_id为0，代表是最后一页的数据
                    max_id = max_id_queue.get(timeout=3)
                    print(f"max_id is: {max_id}")
                    # 此max_id的数据已爬取
                    if max_id in id_list:
                        break
                    comments_params['max_id'] = max_id
                except TimeoutError:
                    break
                id_list.append(max_id)
            else:
                # 代理池的全部ip都无法获取到页面
                raise ProxyException('the proxy pool unavailable...')
    else:
        # 代理获取失败，本机公网ip访问
        while 1:
            # article_id为空则不获取评论数据
            if article_id is None:
                continue

            comments_params['id'] = article_id
            resp = requests.get(url, headers=headers, params=comments_params)
            if resp.status_code == 200:
                data = resp.json()
                # 用一个线程处理每页的数据解析
                t.submit(get_comments_data, data, article_id)

                try:
                    # 循环爬取下一页，直到爬取的页面数据里max_id为0，代表是最后一页的数据
                    max_id = max_id_queue.get(timeout=3)
                    print(f"max_id is: {max_id}")
                    # 此max_id的数据已爬取
                    if max_id in id_list:
                        break
                    comments_params['max_id'] = max_id
                    id_list.append(max_id)
                except TimeoutError as e:
                    print(e)
                    break


def spider(url):
    # 取出文章内容的请求id
    start = url.rfind('/')
    end = url.rfind('?')
    weibo_id = url[start + 1:end]
    print(f'爬取微博：{url}, id是：{weibo_id}' + url)

    # 代理设置
    reset_white_list()
    get_proxy()

    # 文章内容的请求url
    url_article = 'https://weibo.com/ajax/statuses/show'
    # 文章评论的请求url（多条
    url_comments = 'https://weibo.com/ajax/statuses/buildComments'

    headers = {
        'Cookie': 'SINAGLOBAL=5955062269649.503.1700546055600; SCF=Ao7LnEunhbZfNTxau6iJ-p-1P8z0uA3zTwJec__gQT7PpKHoogxooEvbaSzJnnCl-veA43F8nqe-Y8s11tpsh2U.; UOR=,,www.baidu.com; ULV=1711604782369:4:2:2:2981811308310.276.1711604782368:1711007405802; XSRF-TOKEN=1OoNAd9TKELpUymrKgLTqa3n; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpVF02fe0-XSh24So2E; SUB=_2AkMRTbhrdcPxrARZn_4Qy2_iZIlH-jyimNGdAn7uJhMyAxh87lI_qSdutBF-XDq5BJf3e8M1AGbJ2bCm-oBci0RZ; WBPSESS=Dt2hbAUaXfkVprjyrAZT_LBr8_2tpTu-aBOLNGAqe6xJKJj5ECOq7GyUs8CJzYQqJkUQ0mLRbmw0UU3QqGmfbAEKrN4oQFOO_BK1M8zB9FTVsXXRjTLD8UZ5QIJtWqRe35usNF6J1KvocaW1hXzcPb_2zhJbWmuexWX1kEn8WHsxt13B8XNiV_NqyALHGHwL   ',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.0.0 Safari/537.36 '
    }
    article_params = {
        'id': weibo_id,
        'locale': 'zh-CN'
    }

    # 爬取文章评论
    future_spider_comment = t.submit(spider_comments, headers, url_comments)

    # 爬取文章内容
    try:
        article_id = spider_article(headers, url_article, article_params)
    finally:
        conn.close()

    # 阻塞等待全部评论爬取完成
    future_spider_comment.result()
    return article_id

