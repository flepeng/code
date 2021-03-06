# -*- coding:utf-8 -*-
"""
    @Time  : 2021/5/26  17:15
    @Author: Feng Lepeng
    @File  : lstm_text_code.py
    @Desc  :
"""
from __future__ import print_function
import numpy as np
import tensorflow as tf
import random
import collections


def read_data(fname):
    """
    读取fname中的数据
    :param fname:
    :return:
    """
    with open(fname) as f:
        content = f.readlines()
    # 去掉content中每行的前后空格
    content = [x.strip() for x in content]
    # 得到单词
    content_size = len(content)
    words = [content[i].split() for i in range(content_size)]
    words = np.array(words)
    # 将格式转换，认为一行一个样本，一个样本中的序列长度未知，每个时刻一个对应的单词或者符号
    words = np.reshape(words, [-1, ])
    return words


def build_dataset(words):
    """
    构建一个字典和逆字典数据(单词和数字之间的映射关系)
    :param words:
    :return:
    """
    # 计算一下单词的数量(各个单词出现的数量)
    count = collections.Counter(words).most_common()
    # 构建一个字典
    dicts = {}
    k = 0
    for word, _ in count:
        dicts[word] = k
        k += 1
    reverse_dict = dict(zip(dicts.values(), dicts.keys()))
    return dicts, reverse_dict


# 1. 加载数据
training_file = 'belling_the_cat.txt'
training_data = read_data(training_file)
# print(training_data)

# 2. 构建单词和数字之间的映射关系
dict, reverse_dict = build_dataset(training_data)
vocab_size = len(dict)

# 3. 网络参数给定
n_inputs = 3
n_hidden1 = 512
n_hidden2 = 512
n_hidden3 = 128
learn_rate = 0.001
train_iters = 10000

x = tf.placeholder(tf.float32, [None, n_inputs, 1])
y = tf.placeholder(tf.float32, [None, vocab_size])

weights = {
    'out': tf.Variable(tf.random_normal([n_hidden3, vocab_size]))
}
biases = {
    'out': tf.Variable(tf.random_normal([vocab_size]))
}


# 4. 网络构建
def rnn(x):
    # 将数据格式转换一下
    x = tf.reshape(x, [-1, n_inputs])
    # 将数据转换为格式一样的list tensor对象
    x = tf.split(x, n_inputs, 1)

    # 构建细胞
    rnn_cell = tf.nn.rnn_cell.MultiRNNCell(
        cells=[tf.nn.rnn_cell.LSTMCell(num_units=n_hidden1), tf.nn.rnn_cell.GRUCell(num_units=n_hidden2),
               tf.nn.rnn_cell.BasicRNNCell(num_units=n_hidden3)])

    # 构建获取预测值(RNN网络输出的预测值(也就是ppt上写的ht))
    outputs, states = tf.nn.static_rnn(rnn_cell, x, dtype=tf.float32)
    output = outputs[-1]

    # 构建一个隐层到输入层的全连接过程
    return tf.matmul(output, weights['out']) + biases['out']


# 模型构建
pred = rnn(x)

# 定义损失函数
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
train = tf.train.RMSPropOptimizer(learning_rate=learn_rate).minimize(cost)

# 定义准确率
cp = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(cp, tf.float32))

# 运行
with tf.Session() as sess:
    # 变量初始化
    sess.run(tf.global_variables_initializer())
    step = 0
    offset = random.randint(0, n_inputs + 1)
    end_of_offset = n_inputs + 1
    loss_total = 0
    acc_total = 0

    while step < train_iters:
        if offset > (len(training_data) - end_of_offset):
            offset = random.randint(0, n_inputs + 1)
        # 获取inputs个单词，作为输入序列(每个时刻一个单词)
        keys = [[dict[str(training_data[i])]] for i in range(offset, offset + n_inputs)]
        keys = np.reshape(np.array(keys), [-1, n_inputs, 1])
        # print(keys)
        out_onehot = np.zeros([vocab_size], dtype=np.float32)
        out_onehot[dict[str(training_data[offset + n_inputs])]] = 1.0
        out_onehot = np.reshape(out_onehot, [1, -1])
        # print(out_onehot)

        # 训练数据
        _, acc_, cost_, pred_ = sess.run([train, accuracy, cost, pred], feed_dict={x: keys, y: out_onehot})

        acc_total += acc_
        loss_total += cost_
        if (step + 1) % 100 == 0:
            print("Iter:{}, Average Loss:{}，Average Accuracy:{}".format(step + 1, loss_total / 100, acc_total / 100))
            # 测试一下
            symbols_in = [training_data[i] for i in range(offset, offset + n_inputs)]
            symbols_out = training_data[offset + n_inputs]
            symbols_pred = reverse_dict[int(np.argmax(pred_, 1))]
            print("%s - [%s] vs [%s]" % (symbols_in, symbols_out, symbols_pred))
            loss_total = 0
            acc_total = 0

        step += 1
        offset += (n_inputs + 1)

if __name__ == '__main__':
    pass

