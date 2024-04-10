from snownlp import SnowNLP
import csv
import pymysql
import uuid

from snownlp import sentiment
from src.features.features import cutComments
from utils.get_data import getAllComments, getAllArticles


def rateComments(article_id, is_cut=True):
    print('article_id is:', article_id)
    if article_id == "0":
        targetFile = 'target_comment.csv'
        comments = getAllComments()

        rateData = []
        good = 0
        bad = 0
        middle = 0

        for index, comment in enumerate(comments):
            value = SnowNLP(comment[4]).sentiments

            if value < 0.45:
                bad += 1
                rateData.append([comment[4], '负性'])
            elif value >= 0.45 and value <= 0.55:
                middle += 1
                rateData.append([comment[4], '中性'])
            elif value > 0.55:
                good += 1
                rateData.append([comment[4], '正性'])

        with open(targetFile, 'w', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            for rate in rateData:
                writer.writerow(rate)

        # 保存每个情感分类的汇总数据
        with open('stat_rate_comments.csv', 'w', encoding='utf8', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(['good', 'middle', 'bad'])
            writer.writerow([good, middle, bad])
    # 根据文章id从数据库读取评论
    else:
        # print('根据文章id从数据库读取评论...')
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='2280139492',
            database='dr_weibo',
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        query = "SELECT * FROM article_comments WHERE articleId = %s"
        cursor.execute(query, (article_id,))

        # 获取查询结果
        comments = cursor.fetchall()

        good = 0
        bad = 0
        middle = 0


        # 对每条评论数据进行情感极性评分
        for index, comment in enumerate(comments):
            value = SnowNLP(comment[2]).sentiments
            query = "INSERT IGNORE INTO article_comments_sentiment (commentId, articleId, sentiment_score, sentiment_class) VALUES (%s, " \
                    "%s, %s, %s) "

            if value < 0.45:
                bad += 1
                values = (comment[0], article_id, value, '负性')
            elif value >= 0.45 and value <= 0.55:
                middle += 1
                values = (comment[0], article_id, value, '中性')
            elif value > 0.55:
                good += 1
                values = (comment[0], article_id, value, '正性')

            # print('评论内容是：', comment[2])

            # 暂时注释，方便测试代码
            cursor.execute(query, values)
        # 全部评论分词 + 生成词云图
        # print(comments)
        if is_cut:
            cutComments(comments)

        # 提交事务
        conn.commit()

        # 关闭连接
        cursor.close()
        conn.close()



def rateArticles():
    """统计爬取的全部文章情感分类数据"""
    targetFile = 'target_article.csv'
    articles = getAllArticles()

    rateData = []
    good = 0
    bad = 0
    middle = 0

    for index, article in enumerate(articles):
        value = SnowNLP(article[5]).sentiments

        if value < 0.4:
            bad += 1
            rateData.append([article[5], '负性'])
        elif value >= 0.4 and value <= 0.6:
            middle += 1
            rateData.append([article[5], '中性'])
        elif value > 0.6:
            good += 1
            rateData.append([article[5], '正性'])

    with open(targetFile, 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f)
        for rate in rateData:
            writer.writerow(rate)

    # 保存每个情感分类的汇总数据
    with open('stat_rate_articles.csv', 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['good', 'middle', 'bad'])
        writer.writerow([good, middle, bad])


if __name__ == '__main__':
    # 0代表从文件提取
    rateComments("0")
    rateArticles()

