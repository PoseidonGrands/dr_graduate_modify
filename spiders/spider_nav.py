import os, requests, csv
import numpy as np


# 爬取每个分类的链接参数

# 文章数据链接分析
'''
    所有分类的数据
    https://weibo.com/ajax/feed/allGroups
    is_new_segment=1
    fetch_hot=1
'''
'''
    每篇文章的数据
    https://weibo.com/ajax/feed/hottimeline?
    extparam=discover%7Cnew_feed&
    group_id=102803&        哪个分类
    containerid=102803&     哪个分类
         
    其他参数
    refresh=2&
    max_id=1&       第几页
    count=10
'''

def init():
    """初始化数据文件"""

    # 检查文件是否存在
    if not os.path.exists('navData.csv'):
        # 不添加额外的空行
        with open('navData.csv', 'w', encoding='utf-8', newline='') as csvFile:
            # 使用csv模块读写csv文件
            writer = csv.writer(csvFile)
            # typeName根据gid获取
            writer.writerow([
                'typeName',
                'group_id',
                'containerid'
            ])


def writeRow(row):
    """将数据写入数据文件"""
    with open('navData.csv', 'a', encoding='utf-8', newline='') as csvFile:
        # 使用csv模块读写csv文件
        writer = csv.writer(csvFile)

        writer.writerow(row)


def parse_json(data):
    # 获取全部分类的参数数据
    navList = np.append(data['groups'][3]['group'], data['groups'][4]['group'])
    for nav in navList:
        title = nav['title']
        group_id = nav['gid']
        containerid = nav['containerid']

        row = [title, group_id, containerid]

        writeRow(row)


def getData(url):
    headers = {
        'Cookie': 'XSRF-TOKEN=WD2SAKe_HMHSL-eC96RA5db9; login_sid_t=96420783f1229d8df62cd01d8c492d6c; cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=5955062269649.503.1700546055600; SINAGLOBAL=5955062269649.503.1700546055600; ULV=1700546055603:1:1:1:5955062269649.503.1700546055600:; SUB=_2A25IWDYXDeRhGeFG7FQU9yrMwziIHXVrFDffrDV8PUNbmtAGLXfgkW9NeM_WpW37FQwRiAj-iTXomPH-HANVskfi; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5M0en.mmgmPJzsu-lUgbTD5JpX5KzhUgL.FoMRS0qfS0B71hB2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1hMcSKMXehnX; ALF=1732082118; SSOLoginState=1700546120; WBPSESS=rqOJvTwENBgHefuhw6Dmpw-DhEsc7AzZxVffDnsONVAfSHFrbStfFwWA950eb4j_ecbH-IjlKGqyhGaFj0aJbQk4l-neNJwldk11ta9Xm2EWf3Jp_EyxegXy9wAJbS4Jb46Pppkeu0wHbjSwhRGrDw==',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    params = {
        'is_new_segment': 1,
        'fetch_hot': 1
    }

    resp = requests.get(url, headers=headers, params=params)
    print(resp.json())
    if resp.status_code == 200:
        parse_json(resp.json())


if __name__ == '__main__':
    init()

    url = 'https://weibo.com/ajax/feed/allGroups'
    getData(url)

