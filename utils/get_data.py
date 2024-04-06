import ast
import os, requests, csv
from datetime import datetime
import pymysql
from snownlp import SnowNLP

relative_path = '/Users/sewellhe/Py_Projects/ML/dr_graduate/spiders/'
relative_path_src = '/Users/sewellhe/Py_Projects/ML/dr_graduate/src/'


def init_db():
    global conn
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='2280139492',
        database='dr_weibo',
        charset='utf8mb4'
    )


def getAllComments():
    """读取爬取的全部文章的评论数据"""
    comment_list = []

    # 打开 CSV 文件
    with open(relative_path + 'articleCommentsData.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # 可以选择跳过标题行（如果 CSV 文件有标题行）
        next(reader, None)  # 跳过标题行

        for comment in reader:
            comment_list.append(comment)
        return comment_list


def get_comments_all():
    init_db()
    sql = """
        SELECT *
        FROM article_comments
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # print('全部记录', result)
    return result


def get_all_comments(article_id):
    init_db()
    sql = """
        SELECT *
        FROM article_comments
        WHERE articleId = %s;
    """
    cursor = conn.cursor()
    cursor.execute(sql, (article_id,))
    result = cursor.fetchall()
    # print('全部记录', result)
    return result


def get_all_articles():
    init_db()
    sql = """
        SELECT *
        FROM article_content
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # print('全部记录', result)
    return result


def get_sentiment_type_stats(article_id):
    sql = """
            SELECT sentiment_class, COUNT(*) AS count
            FROM article_comments_sentiment
            WHERE articleId = %s
            GROUP BY sentiment_class;
        """
    cursor = conn.cursor()
    cursor.execute(sql, (article_id,))
    result = cursor.fetchall()
    # print("result is:", result)

    article_sentiments_label = []
    article_sentiments_value = []
    article_sentiments = []

    for item in result:
        article_sentiments_label.append(item[0])
        article_sentiments_value.append(item[1])

    print("comment_sentiments_label is:", article_sentiments_label)
    print("comment_sentiments_value is:", article_sentiments_value)

    for i in range(0, len(article_sentiments_label)):
        article_sentiments.append({'name': article_sentiments_label[i], 'value': article_sentiments_value[i]})

    return article_sentiments


def getAllArticles():
    """读取爬取的全部文章的评论数据"""
    article_list = []

    # 打开 CSV 文件
    with open(relative_path + 'articleData.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # 可以选择跳过标题行（如果 CSV 文件有标题行）
        next(reader, None)  # 跳过标题行

        for article in reader:
            article_list.append(article)
        return article_list


def getIndexData():
    """提取全部数据"""

    # 1、提取全部数据
    article_count = 0
    like_count_max = 0
    like_count_max_author = ''
    citys_count = {}
    comments_like_count = []
    date_count = {}
    date_weibo_count = {}
    # 微博的发布日期
    articles_date = {}

    article_list = []
    comment_list = []

    # 读取文章数据
    article_list = getAllArticles()
    # 读取评论数据
    comment_list = getAllComments()

    # 读取文章情感分类汇总数据
    article_sentiments_label = []
    article_sentiments_value = []
    article_sentiments = []
    with open(relative_path_src + 'models/stat_rate_articles.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        article_sentiments_label = next(reader)
        article_sentiments_value = next(reader)

    for i in range(0, len(article_sentiments_label)):
        article_sentiments.append({'name': article_sentiments_label[i], 'value': article_sentiments_value[i]})

    print('article_sentiments is ', article_sentiments)

    # 文章长度
    article_count = len(article_list)

    # 遍历每条文章数据
    for article in article_list:
        if like_count_max < int(article[1]):
            like_count_max = int(article[1])
            like_count_max_author = article[11]

        # 不统计城市数量标记为'无'的数据
        if article[4] != '无':
            # 对字典中还没有的城市加入并统计为1
            if citys_count.get(article[4], -1) == -1:
                citys_count[article[4]] = 1
            # 已存在的城市，对应的数量+1
            else:
                citys_count[article[4]] += 1

        # 获取微博发布日期的日期数据
        if articles_date.get(article[7], -1) == -1:
            articles_date[article[7]] = 1
        else:
            articles_date[article[7]] += 1

    # 排序城市计数字典
    citys_count = list(sorted(citys_count.items(), key=lambda x: x[1], reverse=True))
    # print(citys_count)

    # 获取微博点赞数并排序
    articles_like_count = list(sorted(article_list, key=lambda x: int(x[1]), reverse=True))
    # print(f"articles_like_count: {articles_like_count}")

    # 获取日期（用set去重
    date_count = list(set([article[7] for article in article_list]))
    # 将日期从小到大排序（根据时间戳
    date_count = list(
        sorted(date_count, key=lambda date: datetime.strptime(date, '%Y-%m-%d').timestamp(), reverse=True))
    # print(type(date_count[0]))

    # 获取每个日期对应的微博数量
    '''
        每个索引位置对应着该日期的微博个数
        date_count：['2023-11-23', '2023-11-22', '2023-11-21', ...]
        date_weibo_count:[2, 4, 1, ...]
    '''
    # 初始化长度，长度为统计出来的日期数量
    date_weibo_count = [0 for _ in range(len(date_count))]
    # 查看每篇文章的日期并将对应计数+1
    for article in article_list:
        for index, date in enumerate(date_count):
            if date == article[7]:
                date_weibo_count[index] += 1

    # print(date_count, date_weibo_count)

    # 修改微博发布日期的数据格式
    temp_articles_date = articles_date
    articles_date = []
    for key, value in temp_articles_date.items():
        articles_date.append({
            'name': key,
            'value': value
        })

    articles_type = getArticlesType()
    print(articles_type)

    return article_count, articles_like_count, like_count_max, like_count_max_author, \
           citys_count, date_count, date_weibo_count, articles_type, articles_date, article_sentiments


def get_index_data_all():
    articles_count = 0
    like_count_max = 0
    like_count_max_author = ''
    citys_count = {}
    comments_like_count = []
    date_count = {}
    date_weibo_count = {}
    # 评论的发布日期
    articles_date = {}

    article_list = []
    comment_list = []

    # 初始化数据库
    init_db()
    cursor = conn.cursor()

    # 读取文章数据
    article_list = get_all_articles()
    # 读取评论数据
    sql = """
            SELECT *
            FROM article_comments
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    comment_list = cursor.fetchall()
    print(len(comment_list))

    # 1、读取全部文章的全部评论情感分类汇总数据
    sql = """
                SELECT sentiment_class, COUNT(*) AS count
                FROM article_comments_sentiment
                GROUP BY sentiment_class;
            """
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # print("result is:", result)

    article_sentiments_label = []
    article_sentiments_value = []
    article_sentiments = []

    for item in result:
        article_sentiments_label.append(item[0])
        article_sentiments_value.append(item[1])

    print("comment_sentiments_label is:", article_sentiments_label)
    print("comment_sentiments_value is:", article_sentiments_value)

    for i in range(0, len(article_sentiments_label)):
        article_sentiments.append({'name': article_sentiments_label[i], 'value': article_sentiments_value[i]})
    print(article_sentiments)

    # 2、微博个数
    articles_count = len(article_list)
    print(f'总微博个数有{articles_count}')

    # 3、遍历每条微博数据
    for article in article_list:
        if like_count_max < int(article[2]):
            like_count_max = int(article[2])
            like_count_max_author = article[6]

        # 不统计城市数量标记为'无'的数据
        if article[3] != '无':
            # 对字典中还没有的城市加入并统计为1
            if citys_count.get(article[3], -1) == -1:
                citys_count[article[3]] = 1
            # 已存在的城市，对应的数量+1
            else:
                citys_count[article[3]] += 1

        # 获取微博发布日期的日期数据

        date_str = article[1].strftime("%Y-%m-%d")

        if articles_date.get(date_str, -1) == -1:
            articles_date[date_str] = 1
        else:
            articles_date[date_str] += 1

    # print(like_count_max)
    # print(like_count_max_author)
    # print(citys_count)
    # print(articles_date)

    # 排序城市计数字典
    citys_count = list(sorted(citys_count.items(), key=lambda x: x[1], reverse=True))
    print(citys_count)

    # 获取微博点赞数并排序
    articles_like_count = list(sorted(article_list, key=lambda x: int(x[2]), reverse=True))
    # print(f"comments_like_count: {comments_like_count}")

    # 获取微博发布日期（用set去重
    date_count = list(set([article[1].strftime("%Y-%m-%d") for article in article_list]))
    # print(date_count)
    # 将日期从小到大排序（根据时间戳
    date_count = list(
        sorted(date_count, key=lambda date: datetime.strptime(date, '%Y-%m-%d').timestamp(), reverse=True))
    # print(date_count)

    # 获取每个日期对应的微博数量
    '''
        每个索引位置对应着该日期的微博个数
        date_count：['2023-11-23', '2023-11-22', '2023-11-21', ...]
        date_weibo_count:[2, 4, 1, ...]
    '''
    # 初始化长度，长度为统计出来的日期数量
    date_weibo_count = [0 for _ in range(len(date_count))]
    # 查看每篇文章的日期并将对应计数+1
    for article in article_list:
        for index, date in enumerate(date_count):
            if date == article[1].strftime("%Y-%m-%d"):
                date_weibo_count[index] += 1

    # print(date_count, date_weibo_count)

    # 修改微博发布日期的数据格式
    temp_articles_date = articles_date
    articles_date = []
    for key, value in temp_articles_date.items():
        articles_date.append({
            'name': key,
            'value': value
        })

    print(articles_date)

    # 获取微博类型数据
    articles_type = {}

    # for article in article_list:
    #     # 获取微博类型数据
    #     if articles_type.get(article[8], -1) == -1:
    #         articles_type[article[8]] = 1
    #     else:
    #         articles_type[article[8]] += 1
    #
    # # 修改微博类型的数据格式
    # temp_articles_type = articles_type
    # articles_type = []
    # for key, value in temp_articles_type.items():
    #     articles_type.append({
    #         'name': key,
    #         'value': value
    #     })

    # 读取全部文章的类型汇总数据
    sql = """
                    SELECT type, COUNT(*) as count, SUM(attitudes_count) as total_attitudes
                    FROM article_content WHERE attitudes_count > 5000
                    GROUP BY type ORDER BY count DESC;
                """
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # 只要前10条记录
    result = [result[i] for i in range(0, 10)]
    print("result is:", result)


    article_type_count_gt_5000_label = []
    # 每个类型下点赞数超过5000的记录汇总
    article_type_count_gt_5000_value = []
    article_type_count_gt_5000 = []

    for item in result:
        article_type_count_gt_5000_label.append(item[0])
        article_type_count_gt_5000_value.append(item[1])

    for i in range(0, len(article_type_count_gt_5000_label)):
        article_type_count_gt_5000.append({'name': article_type_count_gt_5000_label[i],
                                           'value': article_type_count_gt_5000_value[i]})
    # print(article_type_count_gt_5000)


    # 提交事务
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()

    return articles_count, articles_like_count, like_count_max, like_count_max_author, \
           citys_count, date_count, date_weibo_count, articles_type, articles_date, article_sentiments,\
           article_type_count_gt_5000


def get_index_data(article_id):
    """提取某条微博数据"""

    comments_count = 0
    like_count_max = 0
    like_count_max_author = ''
    citys_count = {}
    comments_like_count = []
    date_count = {}
    date_weibo_count = {}
    # 评论的发布日期
    comments_date = {}

    article_list = []
    comment_list = []

    # 初始化数据库
    init_db()
    cursor = conn.cursor()

    # 读取评论数据
    comment_list = get_all_comments(article_id)

    # 1、读取该文章的全部评论情感分类汇总数据
    article_sentiments = get_sentiment_type_stats(article_id)
    print('article_sentiments is ', article_sentiments)

    # 2、评论个数
    sql = """
            SELECT COUNT(*) AS count
            FROM article_comments
            WHERE articleId = %s;
        """

    cursor.execute(sql, (article_id,))
    result = cursor.fetchall()
    comments_count = result[0][0]
    print(f'总评论个数有{comments_count}')

    # 3、遍历每条评论数据
    for comment in comment_list:
        if like_count_max < int(comment[3]):
            like_count_max = int(comment[3])
            like_count_max_author = comment[6]

        # 不统计城市数量标记为'无'的数据
        if comment[4] != '无':
            # 对字典中还没有的城市加入并统计为1
            if citys_count.get(comment[4], -1) == -1:
                citys_count[comment[4]] = 1
            # 已存在的城市，对应的数量+1
            else:
                citys_count[comment[4]] += 1

        # 获取微博发布日期的日期数据
        date_str = comment[5].strftime("%Y-%m-%d")
        if comments_date.get(date_str, -1) == -1:
            comments_date[date_str] = 1
        else:
            comments_date[date_str] += 1

    # print(like_count_max)
    # print(like_count_max_author)
    # print(citys_count)
    # print(comments_date)

    # 排序城市计数字典
    citys_count = list(sorted(citys_count.items(), key=lambda x: x[1], reverse=True))
    # print(citys_count)

    # 获取评论点赞数并排序
    comments_like_count = list(sorted(comment_list, key=lambda x: int(x[3]), reverse=True))
    # print(f"comments_like_count: {comments_like_count}")

    # 获取日期（用set去重
    date_count = list(set([comment[5].strftime("%Y-%m-%d") for comment in comment_list]))
    # print(date_count)
    # 将日期从小到大排序（根据时间戳
    date_count = list(
        sorted(date_count, key=lambda date: datetime.strptime(date, '%Y-%m-%d').timestamp(), reverse=True))
    # print(date_count)

    # 获取每个日期对应的微博数量
    '''
        每个索引位置对应着该日期的微博个数
        date_count：['2023-11-23', '2023-11-22', '2023-11-21', ...]
        date_weibo_count:[2, 4, 1, ...]
    '''
    # 初始化长度，长度为统计出来的日期数量
    date_weibo_count = [0 for _ in range(len(date_count))]
    # 查看每篇文章的日期并将对应计数+1
    for comment in comment_list:
        for index, date in enumerate(date_count):
            if date == comment[5].strftime("%Y-%m-%d"):
                date_weibo_count[index] += 1

    # print(date_count, date_weibo_count)

    # 修改微博发布日期的数据格式
    temp_comments_date = comments_date
    comments_date = []
    for key, value in temp_comments_date.items():
        comments_date.append({
            'name': key,
            'value': value
        })

    # print(comments_date)

    articles_type = getArticlesType()
    # print(articles_type)

    # 提交事务
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()

    return comments_count, comments_like_count, like_count_max, like_count_max_author, \
           citys_count, date_count, date_weibo_count, articles_type, comments_date, article_sentiments


def getHotWords():
    with open(relative_path_src + 'features/wordsCount.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()

    # 去除空行
    lines = [line.strip() for line in lines if line.strip()]

    # 将字符串转换成元组
    hotwords = []
    for line in lines:
        # ast.literal_eval将字符串转换成元组
        hotwords.append(ast.literal_eval(line))

    return hotwords


def get_hot_words_all():
    with open(relative_path_src + 'features/wordsCount_all.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()

    # 去除空行
    lines = [line.strip() for line in lines if line.strip()]

    # 将字符串转换成元组
    hotwords = []
    for line in lines:
        # ast.literal_eval将字符串转换成元组
        hotwords.append(ast.literal_eval(line))

    return hotwords


def get_hot_words():
    with open(relative_path_src + 'features/wordsCount_unit.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()

    # 去除空行
    lines = [line.strip() for line in lines if line.strip()]

    # 将字符串转换成元组
    hotwords = []
    for line in lines:
        # ast.literal_eval将字符串转换成元组
        hotwords.append(ast.literal_eval(line))

    return hotwords


def getHotWordAtYear(hotword):
    """获取特定热词在每天的次数"""

    # 发表的微博中出现

    # 评论中出现
    comment_list = getAllComments()
    res = {}
    for comment in comment_list:
        # 该条评论中出现了热词
        if comment[4].find(hotword) != -1:
            if res.get(comment[1], -1) == -1:
                res[comment[1]] = 1
            else:
                res[comment[1]] += 1

    return list(res.keys()), list(res.values())


def get_hotword_at_year(hotword, article_id):
    """获取特定热词在每天的次数"""

    # 发表的微博中出现

    # 评论中出现
    comment_list = get_all_comments(article_id)
    res = {}
    for comment in comment_list:
        # 该条评论中出现了热词
        if comment[2].find(hotword) != -1:
            if res.get(comment[5].strftime("%Y-%m-%d"), -1) == -1:
                res[comment[5].strftime("%Y-%m-%d")] = 1
            else:
                res[comment[5].strftime("%Y-%m-%d")] += 1

    return list(res.keys()), list(res.values())


def get_hotword_at_year_all(hotword):
    """获取特定热词在每天的次数"""

    # 评论中出现
    comment_list = get_comments_all()
    res = {}
    for comment in comment_list:
        # 该条评论中出现了热词
        if comment[2].find(hotword) != -1:
            if res.get(comment[5].strftime("%Y-%m-%d"), -1) == -1:
                res[comment[5].strftime("%Y-%m-%d")] = 1
            else:
                res[comment[5].strftime("%Y-%m-%d")] += 1

    return list(res.keys()), list(res.values())


def getHotWordComment(hotword):
    """获取有出现热词的评论数据"""
    comment_list = getAllComments()

    res = []
    for comment in comment_list:
        if comment[4].find(hotword) != -1:
            res.append(comment)

    return res


def get_hotword_comment(hotword, article_id):
    """获取有出现热词的评论数据"""
    comment_list = get_all_comments(article_id)

    res = []
    for comment in comment_list:
        if comment[2].find(hotword) != -1:
            res.append(comment)

    return res


def get_hotword_comment_all(hotword):
    """获取有出现热词的评论数据"""
    comment_list = get_comments_all()

    res = []
    for comment in comment_list:
        if comment[2].find(hotword) != -1:
            res.append(comment)

    return res


def getopinionStats(flag):
    """获取舆情统计数据"""
    articleList = getAllArticles()

    # 点击了获取情感分类的按钮,给每个文章数据添加一列情感分类的属性
    if flag:
        res = []
        sentiment = ''

        for article in articleList:
            item = list(article)

            sentiment_value = SnowNLP(article[5]).sentiments
            if sentiment_value > 0.45 and sentiment_value < 0.55:
                sentiment = '中性'
            elif sentiment_value >= 0.55:
                sentiment = '正性'
            elif sentiment_value <= 0.45:
                sentiment = '负性'

            item.append(sentiment)
            res.append(item)

        return res
    else:
        return articleList


def get_opinion_Stats(flag, article_id):
    """获取舆情统计数据"""
    comment_list = get_all_comments(article_id)

    # 点击了获取情感分类的按钮,给每个文章数据添加一列情感分类的属性
    if flag:
        res = []
        sentiment = ''

        for comment in comment_list:
            item = list(comment)

            sentiment_value = SnowNLP(comment[2]).sentiments
            if sentiment_value > 0.45 and sentiment_value < 0.55:
                sentiment = '中性'
            elif sentiment_value >= 0.55:
                sentiment = '正性'
            elif sentiment_value <= 0.45:
                sentiment = '负性'

            item.append(sentiment)
            res.append(item)

        return res
    else:
        return comment_list


def get_opinion_Stats_all(flag):
    """获取舆情统计数据"""
    article_list = get_all_articles()

    # 点击了获取情感分类的按钮,给每个文章数据添加一列情感分类的属性
    if flag:
        res = []
        sentiment = ''

        for article in article_list:
            item = list(article)

            sentiment_value = SnowNLP(article[4]).sentiments
            if sentiment_value > 0.45 and sentiment_value < 0.55:
                sentiment = '中性'
            elif sentiment_value >= 0.55:
                sentiment = '正性'
            elif sentiment_value <= 0.45:
                sentiment = '负性'

            item.append(sentiment)
            res.append(item)

        return res
    else:
        return article_list



def getArticlesType():
    """获取微博类型"""
    article_list = getAllArticles()
    articles_type = {}

    for article in article_list:
        # 获取微博类型数据
        if articles_type.get(article[8], -1) == -1:
            articles_type[article[8]] = 1
        else:
            articles_type[article[8]] += 1

    # 修改微博类型的数据格式
    temp_articles_type = articles_type
    articles_type = []
    for key, value in temp_articles_type.items():
        articles_type.append({
            'name': key,
            'value': value
        })

    # print(articles_type)
    return articles_type


def get_articles_type():
    """获取微博类型"""
    article_list = get_all_articles()
    articles_type = {}

    for article in article_list:
        # 获取微博类型数据
        if articles_type.get(article[7], -1) == -1:
            articles_type[article[7]] = 1
        else:
            articles_type[article[7]] += 1

    # 修改微博类型的数据格式
    temp_articles_type = articles_type
    articles_type = []
    for key, value in temp_articles_type.items():
        articles_type.append({
            'name': key,
            'value': value
        })

    # print(articles_type)
    return articles_type


def getLikesCount(type):
    """获取类型为type的微博的点赞数量"""
    article_list = getAllArticles()
    like_count = [int(item[1]) for item in article_list if item[8] == type]
    # print(like_count)

    return like_count

def getCommentsCount(type):
    """获取类型为type的微博的评论数量"""
    article_list = getAllArticles()
    comments_count = [int(item[2]) for item in article_list if item[8] == type]

    print(comments_count)

    return comments_count


def getRepostsCount(type):
    """获取类型为type的微博的转发数量"""
    article_list = getAllArticles()
    reposts_count = [int(item[3]) for item in article_list if item[8] == type]

    # print(reposts_count)

    return reposts_count


def get_likes_Count(type):
    """获取类型为type的微博的点赞数量"""
    article_list = get_all_articles()
    like_count = [int(item[2]) for item in article_list if item[7] == type]
    # print(like_count)

    return like_count


def get_comments_count(type):
    """获取类型为type的微博的评论数量"""
    article_list = get_all_articles()
    comments_count = [int(item[8]) for item in article_list if item[7] == type]

    # print(comments_count)

    return comments_count


def get_reposts_count(type):
    """获取类型为type的微博的转发数量"""
    article_list = get_all_articles()
    reposts_count = [int(item[9]) for item in article_list if item[7] == type]

    print('转发量：', reposts_count)

    return reposts_count


def getRegions():
    """获取微博的发布ip地址"""
    articles = getAllArticles()
    regions = [article[4].strip() for article in articles if article[4] != '']

    print(regions)
    return regions


def get_regions(article_id):
    """获取某微博下全部评论的ip地址"""
    comments = get_all_comments(article_id)
    regions = [comment[4].strip() for comment in comments if comment[4] != '']

    # print(regions)
    return regions


def get_regions_all():
    """获取某微博下全部评论的ip地址"""
    articles = get_all_articles()
    regions = [article[3].strip() for article in articles if article[3] != '']

    init_db()
    query = "SELECT region, COUNT(*) as count FROM article_content GROUP BY region;"
    cursor = conn.cursor()

    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    conn.commit()
    conn.close()

    # print(regions)
    return regions


def get_opinion_data(article_id):
    init_db()
    comment_sentiments = get_sentiment_type_stats(article_id)
    comment_sentiments_label = []
    comment_sentiments_value = []

    for i, v in enumerate(comment_sentiments):
        comment_sentiments_label.append(v['name'])
        comment_sentiments_value.append(v['value'])

    sql = """
        SELECT acs.sentiment_class, SUM(ac.likeCounts) AS total_likeCounts
        FROM article_comments_sentiment acs
        JOIN article_comments ac ON ac.commentId = acs.commentId
        WHERE ac.articleId = %s
        GROUP BY acs.sentiment_class;
    """
    cursor = conn.cursor()
    cursor.execute(sql, (article_id,))
    sentiment_like = cursor.fetchall()
    sentiment_like_label = []
    sentiment_like_value = []

    for i in sentiment_like:
        sentiment_like_label.append(i[0])
        sentiment_like_value.append(int(i[1]))

    print('sentiment_like', sentiment_like)
    print(sentiment_like_label)
    print(sentiment_like_value)

    sql = """
        SELECT
          ac.region,
          acs.sentiment_class,
          COUNT(*) AS sentiment_count
        FROM
          article_comments AS ac
        JOIN
          article_comments_sentiment AS acs
        ON
          ac.commentId = acs.commentId
        WHERE
          ac.articleId = %s
          AND ac.region = %s
        GROUP BY
          ac.region,
          acs.sentiment_class
        ORDER BY
          acs.sentiment_class;
    """
    # 统计全部城市有哪些
    citys_stats = []
    positive = []
    neutral = []
    negative = []
    comments = get_all_comments(article_id)
    for comment in comments:
        if comment[4] != '无':
            # 列表中不存在该城市
            if comment[4] not in citys_stats:
                citys_stats.append(comment[4])

                # 统计该城市的情感分类结果
                # [{'广东':['正性': 2, '中性': 1, ...]}]
                cursor.execute(sql, (article_id, comment[4]))
                result = cursor.fetchall()
                # print(result)
                # break

                positive_count = 0
                neutral_count = 0
                negative_count = 0

                for i in result:
                    if i[1] == '正性':
                        positive_count += i[2]
                    elif i[1] == '负性':
                        negative_count += i[2]
                    elif i[1] == '中性':
                        neutral_count += i[2]
                positive.append(positive_count)
                neutral.append(neutral_count)
                negative.append(negative_count)

    # print(citys_stats)
    # print(positive)
    # print(neutral)
    # print(negative)

    # 获取热词前10
    with open(relative_path_src + 'features/wordsCount_unit.txt', 'r', encoding='utf8') as f:
        words = f.readlines()

    hotwords = []
    hotwords_count = []
    for i in range(0, 10):
        hotwords.append(eval(words[i])[0])
        hotwords_count.append(eval(words[i])[1])

    sentiment_like = cursor.fetchall()

    hotwords = hotwords[::-1]
    hotwords_count = hotwords_count[::-1]

    # print(hotwords)
    # print(hotwords_count)

    return comment_sentiments, comment_sentiments_label, comment_sentiments_value, sentiment_like, \
           sentiment_like_label, sentiment_like_value, citys_stats, positive, neutral, negative, hotwords, \
           hotwords_count
