# -*- coding:utf-8 -*-
"""
    @Time  : 2021/5/26  15:31
    @Author: Feng Lepeng
    @File  : rnn_mnist.py
    @Desc  : 使用RNN实现手写数字识别的功能
"""
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# 数据加载(每个样本都是784维的)
mnist = input_data.read_data_sets('data/', one_hot=True)

# 构建一个会话
with tf.Session() as sess:
    lr = 0.001  # 学习率
    # 每个时刻输入的数据维度大小
    input_size = 28
    # 时刻数目，总共输入多少次
    timestep_size = 28
    # 细胞中一个神经网络的层次中的神经元的数目
    hidden_size = 128
    # RNN中的隐层的数目
    layer_num = 2
    # 最后输出的类别数目
    class_num = 10

    _X = tf.placeholder(tf.float32, [None, 784])
    y = tf.placeholder(tf.float32, [None, class_num])
    # batch_size是一个int32类型的标量tensor的占位符，使用batch_size可以让我们在训练和测试的时候使用不同的数据量
    batch_size = tf.placeholder(tf.int32, [])
    # dropout的时候，保留率多少
    keep_prod = tf.placeholder(tf.float32, [])

    # 开始网络构建
    # 1. 输入的数据格式转换
    # X格式：[batch_size, time_steps, input_size]
    X = tf.reshape(_X, shape=[-1, timestep_size, input_size])

    # # 单层LSTM RNN
    # # 2. 定义cell
    # lstm_cell = tf.nn.rnn_cell.LSTMCell(num_units=hidden_size, reuse=tf.get_variable_scope().reuse)
    #
    # # 3. 单层的RNN网络应用
    # init_state = lstm_cell.zero_state(batch_size, dtype=tf.float32)
    # # time_major=False,默认就是False，output的格式为：[batch_size, timestep_size, hidden_size],
    # # 获取最后一个时刻的输出值是：output_ = output[:,-1,:] 一般就是默认值
    # outputs, state = tf.nn.dynamic_rnn(lstm_cell, inputs=X, initial_state=init_state)
    # output = outputs[:, -1, :]

    # 2. 多层LSTM RNN
    def lstm_cell():
        # 1. 定义cell
        cell = tf.nn.rnn_cell.LSTMCell(hidden_size, reuse=tf.get_variable_scope().reuse)
        # 2. 定义层次与层次之间存在drop out
        # NOTE: drop out只存在于同一时刻的不同layer之间，对于不同时刻，同一layer之间，是不存在drop out的
        return tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=keep_prod)


    # cells参数给定的是每一层的cell，有多少层就给多少个cell，但是cell的类型不做要求
    mulstm_cell = tf.nn.rnn_cell.MultiRNNCell(cells=[lstm_cell() for _ in range(layer_num)])

    # 3. 给定初始化状态信息
    init_state = mulstm_cell.zero_state(batch_size, tf.float32)

    # 4. 构建可以运行的网络结构（假如事件）
    # outputs：格式：[batch_size, timestep_size, hidden_size]
    # state: 格式：[layer_num, 2, batch_size, hidden_size], h_state= state[-1][-1], s_state=state[-1][0]
    outputs, state = tf.nn.dynamic_rnn(mulstm_cell, inputs=X, initial_state=init_state)
    # 得到最后一个时刻对应的输出值
    output = outputs[:, -1, :]

    # 将输出值（最后一个时刻对应的输出值构建为全连接）
    w = tf.Variable(tf.truncated_normal([hidden_size, class_num], mean=0.0, stddev=0.1), dtype=tf.float32, name='out_w')
    b = tf.Variable(tf.constant(0.1, shape=[class_num]), dtype=tf.float32, name='out_b')
    y_pre = tf.nn.softmax(tf.matmul(output, w) + b)

    # 损失函数定义
    loss = -tf.reduce_mean(tf.reduce_sum(y * tf.log(y_pre), 1))
    train = tf.train.AdamOptimizer(learning_rate=lr).minimize(loss)

    # 准确率
    cp = tf.equal(tf.argmax(y_pre, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(cp, tf.float32))

    # 开始训练
    sess.run(tf.global_variables_initializer())
    for i in range(1000):
        _batch_size = 128
        batch = mnist.train.next_batch(_batch_size)
        # 训练模型
        sess.run(train, feed_dict={_X: batch[0], y: batch[1], keep_prod: 0.5, batch_size: _batch_size})
        # 隔一段时间计算准确率
        if (i + 1) % 20 == 0:
            train_acc = sess.run(accuracy,
                                 feed_dict={_X: batch[0], y: batch[1], keep_prod: 1.0, batch_size: _batch_size})
            print("批次:{}, 步骤:{}, 训练集准确率:{}".format(mnist.train.epochs_completed, (i + 1), train_acc))

    # 测试集准确率计算
    test_acc = sess.run(accuracy, feed_dict={_X: mnist.test.images, y: mnist.test.labels, keep_prod: 1.0,
                                             batch_size: mnist.test.num_examples})
    print("测试集准确率:{}".format(test_acc))

if __name__ == '__main__':
    pass
