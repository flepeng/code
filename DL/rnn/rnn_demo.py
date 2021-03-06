# -*- coding:utf-8 -*-
"""
    @Time  : 2021/5/26  15:20
    @Author: Feng Lepeng
    @File  : rnn_demo.py
    @Desc  : TensorFlow中RNN的基础相关概念
             TensorFlow中和RNN相关的API主要位于两个package: tf.nn.rnn_cell(主要定义RNN的常见的几种细胞cell)、tf.nn(RNN相关的辅助操作)
"""
import tensorflow as tf


"""
tf.nn.dynamic_rnn和tf.nn.static_rnn
一般用tf.nn.dynamic_rnn
tf.nn.dynamic_rnn：表示在每个批次中动态的构建rnn执行结构，可以允许在不同时刻传入的数据的特征维度不同，eg: 第一时刻传入的数据格式为:[batch_size, 10], 第二时刻传入的数据格式为:[batch_size, 12], 第三个时刻传入的数据格式为: [batch_size, 8]......；默认就是填0.
tf.nn.static_rnn: 在网络执行前，就构建好rnn的执行结构，要求传入的数据长度必须一致，而且传入的数据必须是tensor的list集合；构建的时候比较慢，但是执行相对比较快。
"""

# 一、RNN的中的细胞Cell
# 基类：tf.nn.rnn_cell.RNNCell
# 最基本的RNN的实现Cell：tf.nn.rnn_cell.BasicRNNCell
# 简单的LSTM Cell实现：tf.nn.rnn_cell.BasicLSTMCell
# 最常用的LSTM Cell实现： tf.nn.rnn_cell.LSTMCell
# GRU Cell实现：tf.nn.rnn_cell.GRUCell
# 多层RNN结构网络的实现：tf.nn.rnn_cell.MultiRNNCell
# 定义cell
# num_units：给定一个细胞中的各个神经层次中的神经元数目（状态维度和输出的数据维度和num_units一致）,输出的维度数
# cell = tf.nn.rnn_cell.BasicRNNCell(num_units=128)
# print(cell.state_size)
# print(cell.output_size)
#
# # 4表示的是每个时刻输入4个样本，64表示每个样本具有64维的特征
# inputs = tf.placeholder(tf.float32, shape=(4, 64))
# # 给定RNN的初始状态,4表示每个时刻输入的样本数目
# # s0的状态是: (batch_size, state_size)
# s0 = cell.zero_state(4, tf.float32)
# print(s0.get_shape())
# # 对于t=1时刻传入输入和state获取结果值
# output, s1 = cell.call(inputs, s0)
# print(s1.get_shape())
# print(output.get_shape())

# # 定义lstm cell
# lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=128)
# # 4表示的是每个时刻输入4个样本，64表示每个样本具有64维的特征
# inputs = tf.placeholder(tf.float32, shape=(4, 64))
# # 给定RNN的初始状态,4表示每个时刻输入的样本数目
# # s0的状态是: (batch_size, state_size)
# s0 = lstm_cell.zero_state(4, tf.float32)
# print(s0.h.get_shape())
# print(s0.c.get_shape())
# # 对于t=1时刻传入输入和state获取结果值(LSTM中存在两个传入到下一个时刻的隐状态，即：C和h，在API中，全部都存储于s1中)
# output, s1 = lstm_cell.call(inputs, s0) # ===> 等价于output, s1 = lstm_cell(inputs, s0)
# print(s1.h.get_shape())
# print(s1.c.get_shape())
# print(output.get_shape())

# 一次多步的执行
# 因为cell.call方法，需要每个时刻均调用一次，比较麻烦
# cell: RNNCell对象
# inputs: 输入信息，一组序列(从t=0到t=T), 格式要求：[batch_size, time_steps, input_size]，batch_size: 每个时刻输入的样本数目，time_steps: 序列从长度（时间长度），input_size: 输入数据中单个样本的维度数量
# initial_state: 初始状态，一般为0矩阵
# 返回：output: time_steps所有的输出，格式为: [batch_size, time_steps, output_size]
# 返回：state：最后一步的状态，格式为: [batch_size, state_size]
# output, state = tf.nn.dynamic_rnn(cell, inputs, initial_state=initial_state)

if __name__ == '__main__':
    pass
