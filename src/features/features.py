import os
import re

import numpy as np
import pandas as pd
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

from utils.get_data import getAllComments, get_all_comments
from utils.get_data import getAllArticles

import jieba
import jieba.analyse as analyse


targetTxt = 'cutWords.txt'

def stopWordList():
    stop_words = [line.strip() for line in open('./baidu_stopwords.txt', encoding='utf8').readlines()]
    return stop_words


def filter_stopwords(comments):
    """去除停用词"""

    # 对评论内容进行分词，每个词用空格分开
    comments_cut = jieba.cut(" ".join([comment[4] for comment in comments]).strip())

    # print(" ".join([comment[4] for comment in comments]).strip())

    # 去除停用词
    res = ''
    stop_words = stopWordList()

    for word in comments_cut:
        # print(word)
        if word not in stop_words:
            res += word

    # print(res)
    return res


def cutWords():
    """分词并写入文件"""
    with open(targetTxt, 'w', encoding='utf-8') as targetFile:
        # 全模式分词
        seg = jieba.cut(filter_stopwords(getAllComments()), cut_all=True)

        res = " ".join(seg)
        targetFile.write(res)

        targetFile.write('\n')
        print('写入完成')


def cutComments(comments):
    if len(comments) == 0:
        return
    print("当前目录：", os.getcwd())
    # 1、分词
    cut = jieba.cut(" ".join([comment[2] for comment in comments]).strip())
    print('分词结果为', cut)

    # 2、去除停用词
    res = ''
    stop_words = [line.strip() for line in open('/Users/sewellhe/Py_Projects/ML/dr_graduate/src/features/baidu_stopwords.txt', encoding='utf8').readlines()]
    custom_stop_words = ['http', 'cn']

    for word in cut:
        # print(word)
        if word not in stop_words and word not in custom_stop_words:
            res += word

    # 3、再次分词、保存结果
    with open('/Users/sewellhe/Py_Projects/ML/dr_graduate/src/features/cutWords_unit.txt', 'w', encoding='utf-8') as targetFile:
        # 全模式分词
        seg = jieba.cut(res, cut_all=True)

        res = " ".join(seg)
        targetFile.write(res)

        targetFile.write('\n')
        print('写入完成')

    # 4、过滤
    reader = open('/Users/sewellhe/Py_Projects/ML/dr_graduate/src/features/cutWords_unit.txt', 'r', encoding='utf8')
    strs = reader.read()
    result = open('/Users/sewellhe/Py_Projects/ML/dr_graduate/src/features/wordsCount_unit.txt', 'w', encoding='utf8')

    # 此处再次分词只是为了能循环遍历每个词
    words = jieba.cut(strs, cut_all=True)

    new_words = []
    for word in words:
        # 去除数字、标点符号
        match_1 = re.search('\d+', word)
        match_2 = re.search('\W+', word)

        # 匹配成功返回match对象，否则返回None
        if (not match_1) and (not match_2) and word != '' and len(word) > 1:
            # 不包含标点符号或数字则保留
            new_words.append(word)

    # 5、词频统计
    word_count = {}
    for i in new_words:
        word_count[i] = new_words.count(i)

    word_count_sorted = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    # 过滤词频为1的数据
    word_count_sorted = [item for item in word_count_sorted if item[1] > 1]

    # 将词频统计结果写入文件
    for i in word_count_sorted:
        print(i, file=result)

    # 6、生成词云图
    font_path = '/Users/sewellhe/Py_Projects/ML/dr_graduate/src/features/wendaoshouyuanti.ttf'
    mask = np.array(Image.open('/Users/sewellhe/Py_Projects/ML/dr_graduate/src/features/weibo_wordcloud_bg_pixian_ai.png'))
    wordcloud = WordCloud(font_path=font_path,
                          background_color="white",
                          mask=mask,
                          width=800,
                          height=600,
                          stopwords=set(stop_words),
                          contour_color='gray',  # 设置词云边框颜色
                          contour_width=1,  # 设置词云边框宽度 0是没有边框 一般用在指定形状的词云设置中
                          colormap=None,  # 设置组成词云的字体的颜色
                          color_func=None,  # 设置根据某种模式设置组成词云的字体颜色 比如根据图片的颜色对应设置词云颜色
                          max_words=200,  # 设置最多显示多少个词 默认是200
                          max_font_size=80,  # 设置最大的字体字号
                          min_font_size=2,  # 设置最小的字体字号
                          scale=1  # 缩放比例 一般 1~4 即可 避免分辨率不够导致有些字太小看不清
                          )
    data = ' '.join(new_words)
    wordcloud.generate(data)
    # wordcloud.to_file('src/features/wordCloud_unit.jpg')
    wordcloud.to_file('/Users/sewellhe/Py_Projects/ML/dr_graduate/flask_app/resources/static/image/wordCloud_unit.jpg')


def cut_comments_all(comments):

    # 1、分词
    cut = jieba.cut(" ".join([comment[2] for comment in comments]).strip())
    print('分词结果为', cut)

    # 2、去除停用词
    res = ''
    stop_words = [line.strip() for line in open('../src/features/baidu_stopwords.txt', encoding='utf8').readlines()]
    custom_stop_words = ['http', 'cn']

    for word in cut:
        # print(word)
        if word not in stop_words and word not in custom_stop_words:
            res += word



    # 3、再次分词、保存结果
    with open('../src/features/cutWords_all.txt', 'w', encoding='utf-8') as targetFile:
        # 全模式分词
        seg = jieba.cut(res, cut_all=True)

        res = " ".join(seg)
        targetFile.write(res)

        targetFile.write('\n')
        print('写入完成')

    # 4、过滤
    reader = open('../src/features/cutWords_all.txt', 'r', encoding='utf8')
    strs = reader.read()
    result = open('../src/features/wordsCount_all.txt', 'w', encoding='utf8')
    print('过滤完成...')
    # 此处再次分词只是为了能循环遍历每个词
    words = jieba.cut(strs, cut_all=True)

    new_words = []
    for word in words:
        # 去除数字、标点符号
        match_1 = re.search('\d+', word)
        match_2 = re.search('\W+', word)

        # 匹配成功返回match对象，否则返回None
        if (not match_1) and (not match_2) and word != '' and len(word) > 1:
            # 不包含标点符号或数字则保留
            new_words.append(word)

    # print(new_words)
    # 5、词频统计
    words_np = np.array(new_words)
    word_count = pd.Series(words_np).value_counts()

    # word_count = {}
    # for i in new_words:
    #     # new_words的值为键，值为在new_words出现的次数
    #     word_count[i] = new_words.count(i)

    print(word_count)

    word_count_sorted = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    # 只要词频统计前100的词
    # word_count_sorted = [item for item in word_count_sorted if item[1] > 100]
    word_count_sorted = [word_count_sorted[i] for i in range(0, 100)]
    print(word_count_sorted)


    # 将词频统计结果写入文件
    for i in word_count_sorted:
        print(i, file=result)
    print('词频统计完成...')

    # 6、生成词云图
    font_path = '../src/features/wendaoshouyuanti.ttf'
    mask = np.array(Image.open('../src/features/weibo_wordcloud_bg_pixian_ai.png'))
    wordcloud = WordCloud(font_path=font_path,
                          background_color="white",
                          mask=mask,
                          width=800,
                          height=600,
                          stopwords=set(stop_words),
                          contour_color='gray',  # 设置词云边框颜色
                          contour_width=1,  # 设置词云边框宽度 0是没有边框 一般用在指定形状的词云设置中
                          colormap=None,  # 设置组成词云的字体的颜色
                          color_func=None,  # 设置根据某种模式设置组成词云的字体颜色 比如根据图片的颜色对应设置词云颜色
                          max_words=80,  # 设置最多显示多少个词 默认是200
                          max_font_size=80,  # 设置最大的字体字号
                          min_font_size=2,  # 设置最小的字体字号
                          scale=1  # 缩放比例 一般 1~4 即可 避免分辨率不够导致有些字太小看不清
                          )
    data = ' '.join(new_words)
    wordcloud.generate(data)
    wordcloud.to_file('../src/features/wordCloud_all.jpg')
    wordcloud.to_file('../flask_app/resources/static/image/wordCloud_all.jpg')




if __name__ == '__main__':
    # 分词
    cutWords()

    reader = open('./cutWords.txt', 'r', encoding='utf8')
    strs = reader.read()
    result = open('./wordsCount.txt', 'w', encoding='utf8')

    # 此处再次分词只是为了能循环遍历每个词
    words = jieba.cut(strs, cut_all=True)

    new_words = []

    # 过滤
    for word in words:
        # 去除数字、标点符号
        match_1 = re.search('\d+', word)
        match_2 = re.search('\W+', word)

        # 匹配成功返回match对象，否则返回None
        if (not match_1) and (not match_2) and word != '':
            # 不包含标点符号或数字则保留
            new_words.append(word)

    # 词频统计
    word_count = {}
    for i in new_words:
        word_count[i] = new_words.count(i)

    word_count_sorted = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    # 过滤词频为1的数据
    word_count_sorted = [item for item in word_count_sorted if item[1] > 1]

    # 将词频统计结果写入文件
    for i in word_count_sorted:
        print(i, file=result)


    # 生成词云图
    font_path = 'wendaoshouyuanti.ttf'
    mask = np.array(Image.open('weibo_wordcloud_bg_pixian_ai.png'))
    wordcloud = WordCloud(font_path='wendaoshouyuanti.ttf',
                          background_color="white",
                          mask=mask,
                          width=800,
                          height=600,
                          stopwords=set(stopWordList()),
                          contour_color='gray',  # 设置词云边框颜色
                          contour_width=1,  # 设置词云边框宽度 0是没有边框 一般用在指定形状的词云设置中
                          colormap=None,  # 设置组成词云的字体的颜色
                          color_func=None,  # 设置根据某种模式设置组成词云的字体颜色 比如根据图片的颜色对应设置词云颜色
                          max_words=200,  # 设置最多显示多少个词 默认是200
                          max_font_size=80,  # 设置最大的字体字号
                          min_font_size=2,  # 设置最小的字体字号
                          scale=1  # 缩放比例 一般 1~4 即可 避免分辨率不够导致有些字太小看不清
                          )
    data = ' '.join(new_words)
    wordcloud.generate(data)
    wordcloud.to_file('wordCloud.jpg')

    # print(strs)

    # print(' '.join(new_words))
    # print(new_words)
    # print(word_count)
    print(word_count_sorted)







