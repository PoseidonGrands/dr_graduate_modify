import numpy as np
from flask import render_template, redirect, url_for, Blueprint, flash, session, request

from flask_app.accounts.form import RegisterForm, LoginForm
from flask_app.model.accounts import User, db

from snownlp import SnowNLP

from wordcloud import WordCloud

from spiders.spider_target_article import spider
from src.models.yuqing import rateComments
from utils.get_data import getIndexData, getHotWords, getHotWordAtYear, getHotWordComment, getopinionStats, \
    getArticlesType, getLikesCount, getCommentsCount, getRepostsCount, getRegions, get_index_data, get_hot_words, \
    get_hotword_at_year, get_hotword_comment, get_opinion_Stats, get_regions, get_opinion_data, get_index_data_all, \
    get_regions_all, get_hot_words_all, get_hotword_at_year_all, get_hotword_comment_all, get_opinion_Stats_all, \
    get_articles_type, get_likes_Count, get_comments_count, get_reposts_count

manage = Blueprint('manage', __name__, template_folder='templates', static_folder='resources/static')

# 拦截未登录用户
# before_request

print('页面刷新了...')
article_id = "0"
# article_id = "4988739196027315"

@manage.route('/<int:item_id>')
def index(item_id):
    # 从数据库获取用户对象
    # ...
    global article_id
    print('article_id is:', article_id)

    if request.args.get('getAllData'):
        article_id = "0"

    # 从请求参数获取需要分析的url并分析数据
    if request.args.get('url'):
        print(request.args.get('url'))
        # 1、爬取该微博的数据
        article_id = spider(request.args.get('url'))
        # article_id = '4986914584920686'
        # print(article_id)
        # 2、对这些数据做情感分析
        rateComments(article_id)

        # 3、展示
        comments_count, comments_like_count, like_count_max, like_count_max_author, \
        citys_count, date_count, date_weibo_count, articles_type, articles_date, \
        article_sentiments = get_index_data(article_id)


        return render_template('index.html',
                               is_get_url=1,
                               item_id=item_id,
                               article_count=comments_count,
                               comments_like_count=comments_like_count,
                               like_count_max=like_count_max,
                               like_count_max_author=like_count_max_author,
                               citys_count=citys_count,
                               date_count=date_count,
                               date_weibo_count=date_weibo_count,
                               articles_type=articles_type,
                               articles_date=articles_date,
                               article_sentiments=article_sentiments)
    elif article_id != "0":
        rateComments(article_id)

        # 3、展示
        comments_count, comments_like_count, like_count_max, like_count_max_author, \
        citys_count, date_count, date_weibo_count, articles_type, articles_date, \
        article_sentiments = get_index_data(article_id)

        return render_template('index.html',
                               is_get_url=1,
                               item_id=item_id,
                               article_count=comments_count,
                               comments_like_count=comments_like_count,
                               like_count_max=like_count_max,
                               like_count_max_author=like_count_max_author,
                               citys_count=citys_count,
                               date_count=date_count,
                               date_weibo_count=date_weibo_count,
                               articles_type=articles_type,
                               articles_date=articles_date,
                               article_sentiments=article_sentiments)
    else:
        # 获取并分析全部数据
        article_count, articles_like_count, like_count_max, like_count_max_author, \
        citys_count, date_count, date_weibo_count, articles_type, articles_date, \
        article_sentiments, article_type_count_gt_5000 = get_index_data_all()

        return render_template('index.html',
                               is_get_url=0,
                               item_id=item_id,
                               article_count=article_count,
                               articles_like_count=articles_like_count,
                               like_count_max=like_count_max,
                               like_count_max_author=like_count_max_author,
                               citys_count=citys_count,
                               date_count=date_count,
                               date_weibo_count=date_weibo_count,
                               articles_type=articles_type,
                               articles_date=articles_date,
                               article_sentiments=article_sentiments,
                               article_type_count_gt_5000=article_type_count_gt_5000
                               )


@manage.route('/hotWordStatistics/<int:item_id>')
def hotWordStatistics(item_id):
    """热词统计"""

    # print('hotWordStatistics id：', article_id)

    if article_id != "0":
        hotwords = get_hot_words()
    else:
        hotwords = get_hot_words_all()
    # 展示选中的热词（如果选中了，则重新请求页面，参数为选择的热词
    selected_hotword = hotwords[0][0]
    print('selected_hotword is:', selected_hotword)
    if request.args.get('hotWord'):
        selected_hotword = request.args.get('hotWord')
    sentiment = ''
    sentiment_value = SnowNLP(selected_hotword).sentiments
    if sentiment_value > 0.45 and sentiment_value < 0.55:
        sentiment = '中性'
    elif sentiment_value >= 0.55:
        sentiment = '正性'
    elif sentiment_value <= 0.45:
        sentiment = '负性'

    if article_id != "0":
        # 热词在每天出现的次数(评论
        xData, yData = get_hotword_at_year(selected_hotword, article_id)

        # 热词出现的评论
        hotWord_comments = get_hotword_comment(selected_hotword, article_id)
    else:
        # 热词在每天出现的次数(评论
        xData, yData = get_hotword_at_year_all(selected_hotword)

        # 热词出现的评论
        hotWord_comments = get_hotword_comment_all(selected_hotword)


    return render_template('hotword.html',
                           is_get_url=1 if article_id != "0" else 0,
                           item_id=item_id,
                           hotwords=hotwords,
                           selected_hotword=selected_hotword,
                           sentiment=sentiment,
                           xData=xData,
                           yData=yData,
                           hotWord_comments=hotWord_comments)


@manage.route('/opinionStatistics/<int:item_id>')
def opinionStatistics(item_id):
    """舆情统计"""

    # 是否展示情感分类
    default_flag = False

    # 获取请求参数flag：True为展示情感分类
    if request.args.get('flag'):
        if request.args.get('flag') == 'True':
            default_flag = True
        elif request.args.get('flag') == 'False':
            default_flag = False

    print('oponionStats id：', article_id)

    # 查看某微博数据
    if article_id != "0":
        # 获取某篇微博数据
        data = get_opinion_Stats(default_flag, article_id)

        return render_template('opinionStats.html',
                               is_get_url=1,
                               item_id=item_id,
                               default_flag=default_flag,
                               data=data)
    else:
        # 获取全部微博数据
        data = get_opinion_Stats_all(default_flag)

        return render_template('opinionStats.html',
                               is_get_url=0,
                               item_id=item_id,
                               default_flag=default_flag,
                               data=data)


@manage.route('/articleAnalysis/<int:item_id>')
def articleAnalysis(item_id):
    """文章分析"""
    print('文章分析', article_id)
    articles_type = get_articles_type()

    # 选择的文章类型
    # 默认文章类型
    selected_article_type = articles_type[0]['name']
    # 从请求参数中获取文章类型
    if request.args.get('articleType'):
        selected_article_type = request.args.get('articleType')

    # 1、统计对应文章类型的点赞数（不同类型的文章点赞数分布的差别太大，采用分位数分区间来分析
    like_count = get_likes_Count(selected_article_type)

    # 1.1、划分点赞数区间
    start = round(min(like_count))
    end = round(max(like_count))
    step = round((end - start) / 6)

    scope_likes = [start]
    for i in range(5):
        scope_likes.append(scope_likes[i] + step)
    scope_likes.append(end)
    # print(scope_likes)

    scope_like_label = [f"0-{scope_likes[0]}"]
    [scope_like_label.append(f"{scope_likes[i]}-{scope_likes[i + 1]}") for i in range(0, 6)]

    # 1.2、统计每个区间内的评论数量
    counts_like = [0 for i in range(7)]
    # 遍历全部评论数
    for i in like_count:
        # for i in [600, 500, 100, 1200]:
        # 寻找此评论数所在区间
        for index, j in enumerate(scope_likes):
            # 左开右闭区间
            if i <= scope_likes[index]:
                if index != 0:
                    counts_like[index] += 1
                else:
                    counts_like[0] += 1
                break
    """
    # 计算七个区间的分位数
    quantiles = np.quantile(like_count, [i / 7 for i in range(1, 8)])
    quantiles = [round(i) for i in quantiles]
    # print(quantiles)

    scope_like_label = [f"0-{quantiles[0]}"]
    [scope_like_label.append(f"{quantiles[i]}-{quantiles[i + 1]}") for i in range(0, 6)]

    # print(scope)

    # 1.2、计算每个区间的数据量
    counts_like = [0 for i in range(7)]
    # 遍历全部点赞数
    for i in like_count:
        # 寻找此点赞数所在区间
        for index, j in enumerate(quantiles):
            # 左开右闭区间
            if i <= quantiles[index]:
                if index != 0:
                    counts_like[index] += 1
                else:
                    counts_like[0] += 1
                break
    # print(counts)
    """

    # 2、统计对应文章类型的评论数（评论数不会特别多，采用最大最小值间平均分7个区间，离散值不大
    # 对应文章类型的评论数
    comment_count = get_comments_count(selected_article_type)


    # 2.1、划分评论量区间
    start = round(min(comment_count))
    end = round(max(comment_count))
    step = round((end - start) / 6)

    scope_comments = [start]
    for i in range(5):
        scope_comments.append(scope_comments[i] + step)
    scope_comments.append(end)
    # print(scope_comments)

    scope_comment_label = [f"0-{scope_comments[0]}"]
    [scope_comment_label.append(f"{scope_comments[i]}-{scope_comments[i + 1]}") for i in range(0, 6)]

    # 2.2、统计每个区间内的评论数量
    counts_comment = [0 for i in range(7)]
    # 遍历全部评论数
    for i in comment_count:
    # for i in [600, 500, 100, 1200]:
        # 寻找此评论数所在区间
        for index, j in enumerate(scope_comments):
            # 左开右闭区间
            if i <= scope_comments[index]:
                if index != 0:
                    counts_comment[index] += 1
                else:
                    counts_comment[0] += 1
                break

    # 3、统计对应文章类型的转发量
    # 对应文章类型的评论数
    reposts_count = get_reposts_count(selected_article_type)

    # 3.1、划分区间
    scope_repost = []   # 区间分割值
    for i in range(1, int(5000 / 50)):
        scope_repost.append(i * 50)

    scope_repost_label = [f"0-{scope_repost[0]}"]   # 区间标签值
    [scope_repost_label.append(f"{scope_repost[i]}-{scope_repost[i + 1]}") for i in range(len(scope_repost) - 1)]

    print(scope_repost)
    print(scope_repost_label)

    # 3.2、分类
    counts_repost = [0 for _ in range(len(scope_repost_label))]
    for i in reposts_count:
        # 寻找此转发数所在区间
        for index, j in enumerate(scope_repost):
            # 左开右闭区间
            if i <= scope_repost[index]:
                if index != 0:
                    counts_repost[index] += 1
                else:
                    counts_repost[0] += 1
                break
    print('counts_repost:', counts_repost)

    return render_template('articleAnalysis.html',
                           item_id=item_id,
                           is_get_url=0,
                           selected_article_type=selected_article_type,
                           articles_type=articles_type,
                           scope_like_label=scope_like_label,
                           counts_like=counts_like,
                           scope_comment_label=scope_comment_label,
                           counts_comment=counts_comment,
                           scope_repost_label=scope_repost_label,
                           counts_repost=counts_repost)


@manage.route('/ipAnalysis/<int:item_id>')
def ipAnalysis(item_id):
    """ip分析"""

    # 查看某微博数据
    if article_id != "0":
        regions = get_regions(article_id)
        counts_region = {}
        for region in regions:
            if counts_region.get(region, -1) == -1:
                counts_region[region] = 1
            else:
                counts_region[region] += 1
        print(counts_region)

        return render_template('ipAnalysis.html',
                               is_get_url=1,
                               item_id=item_id,
                               counts_region=counts_region)
    else:
        regions = get_regions_all()
        counts_region = {}
        for region in regions:
            if counts_region.get(region, -1) == -1:
                counts_region[region] = 1
            else:
                counts_region[region] += 1
        print(counts_region)

        return render_template('ipAnalysis.html',
                               is_get_url=0,
                               item_id=item_id,
                               counts_region=counts_region)


def commentAnalysis():
    """评论分析"""

@manage.route('/opinionAnalysis/<int:item_id>')
def opinionAnalysis(item_id):
    """舆情分析"""

    if article_id != "0":
        comment_sentiments, comment_sentiments_label, comment_sentiments_value, sentiment_like,\
        sentiment_like_label, sentiment_like_value, citys_stats, positive, neutral, negative,\
        hotwords, hotwords_count = get_opinion_data(article_id)
        return render_template('opinionAnalysis.html',
                               is_get_url=1,
                               item_id=item_id,
                               comment_sentiments_label=comment_sentiments_label,
                               comment_sentiments_value=comment_sentiments_value,
                               sentiment_like=sentiment_like,
                               sentiment_like_label=sentiment_like_label,
                               sentiment_like_value=sentiment_like_value,
                               citys_stats=citys_stats,
                               positive=positive,
                               neutral=neutral,
                               negative=negative,
                               hotwords=hotwords,
                               hotwords_count=hotwords_count)

@manage.route('/commentsWordCloud/<int:item_id>')
def wordCloud(item_id):
    """评论内容词云图"""
    return render_template('commentsWordCloud.html',
                           item_id=item_id,
                           is_get_url=1 if article_id != "0" else 0)



@manage.route('/logout')
def logout():
    session.clear()

    # 路径为蓝图注册时accounts的访问路径
    return redirect('/accounts/login')
