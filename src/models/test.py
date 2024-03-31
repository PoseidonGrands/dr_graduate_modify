from snownlp import sentiment

import io
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        return chardet.detect(file.read())['encoding']


# print(detect_encoding('neg60000.txt'))
# print(detect_encoding('pos60000.txt'))


def read_file(file_path, encoding, error_handling='replace'):
    with io.open(file_path, 'r', encoding=encoding, errors=error_handling) as f:
        return f.read()


# neg = read_file('neg60000.txt', 'GB2312', 'replace')
# pos = read_file('pos60000.txt', 'GB2312', 'replace')

# neg = read_file('neg6.txt', 'GB2312', 'replace')
# pos = read_file('pos6.txt', 'GB2312', 'replace')
# print(neg)
# sentiment.train(neg, pos)

sentiment.train('neg60000.txt', 'pos60000.txt')
sentiment.save('sentiment.marshal.3')

