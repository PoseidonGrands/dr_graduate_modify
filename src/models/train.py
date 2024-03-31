import pandas as pd
import numpy as np
import csv

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB

from sklearn.neighbors import NearestNeighbors


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.metrics import classification_report

"""
    手写模型，未实现
"""

if __name__ == '__main__':
    sentiment_data = []
    with open('./target.csv', 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for data in reader:
            sentiment_data.append(data)

    print(sentiment_data)

    df = pd.DataFrame(sentiment_data, columns=['comment', 'rate'])
    label_mapping = {
        '正性': 1,
        '中性': 0,
        '负性': -1
    }
    y = df['rate'].replace(label_mapping)

    vectorizer = TfidfVectorizer()
    x = vectorizer.fit_transform(df['comment'])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # 模型训练
    classifier = MultinomialNB()
    classifier.fit(x_train, y_train)

    # 使用训练好的模型预测数据
    y_pred = classifier.predict(x_test)

    # 准确度
    accuracy = accuracy_score(y_pred, y_test)
    print(accuracy)
