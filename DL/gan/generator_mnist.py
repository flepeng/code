# -*- coding:utf-8 -*-
"""
    @Time  : 2021/5/27  18:42
    @Author: Feng Lepeng
    @File  : generator_mnist.py
    @Desc  : GAN生成手写数字图片
"""
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import os
import shutil
import numpy as np
from skimage.io import imsave

checkpoint_dir = "output"
is_restore = True
image_height = 28
image_weight = 28
image_size = image_height * image_weight
h1_size = 150
h2_size = 300
z_size = 100
batch_size = 256
max_epoch = 500


def build_generator(z_prior):
    """
    构建G网络
    :param z_prior: 输入的噪音数据, 是一个Tensor对象, n行z_size列的数据，n行表示n个样本输入，z_size表示每个输入的样本的维度大小
    :return:
    """
    # 2. 第一层：Hidden layer
    w1 = tf.Variable(tf.truncated_normal([z_size, h1_size], stddev=0.1), name='g_w1', dtype=tf.float32)
    b1 = tf.Variable(tf.zeros([h1_size]), name='g_b1', dtype=tf.float32)
    h1 = tf.nn.relu(tf.matmul(z_prior, w1) + b1)

    # 3. 第二层：Hidden layer
    w2 = tf.Variable(tf.truncated_normal([h1_size, h2_size], stddev=0.1), name='g_w2', dtype=tf.float32)
    b2 = tf.Variable(tf.zeros([h2_size]), name='g_b2', dtype=tf.float32)
    h2 = tf.nn.relu(tf.matmul(h1, w2) + b2)

    # 4. 第三层：准备输出
    w3 = tf.Variable(tf.truncated_normal([h2_size, image_size], stddev=0.1), name='g_w3', dtype=tf.float32)
    b3 = tf.Variable(tf.zeros([image_size]), name='g_b3', dtype=tf.float32)
    h3 = tf.nn.tanh(tf.matmul(h2, w3) + b3)

    return h3, [w1, b1, w2, b2, w3, b3]


def build_disciminator(x_data, x_generated, keep_prob):
    """
    构建一个判别模型
    :param x_data:  真实数据
    :param x_generated: 假数据
    :param keep_prob: 进行drop out的时候给定的保留率
    :return:
    """
    # 1. 合并训练数据
    x_input = tf.concat([x_data, x_generated], 0)

    # 2. 第一层：Hidden Layer
    w1 = tf.Variable(tf.truncated_normal([image_size, h2_size], stddev=0.1), name='d_w1', dtype=tf.float32)
    b1 = tf.Variable(tf.zeros([h2_size]), name='d_b1', dtype=tf.float32)
    h1 = tf.nn.dropout(tf.nn.relu(tf.matmul(x_input, w1) + b1), keep_prob)

    # 3. 第二层：Hidden Layer
    w2 = tf.Variable(tf.truncated_normal([h2_size, h1_size], stddev=0.1), name='d_w2', dtype=tf.float32)
    b2 = tf.Variable(tf.zeros([h1_size]), name='d_b2', dtype=tf.float32)
    h2 = tf.nn.dropout(tf.nn.relu(tf.matmul(h1, w2) + b2), keep_prob)

    # 3. 第三层：Hidden Layer(准备输出)
    w3 = tf.Variable(tf.truncated_normal([h1_size, 1], stddev=0.1), name='d_w3', dtype=tf.float32)
    b3 = tf.Variable(tf.zeros([1]), name='d_b3', dtype=tf.float32)
    h3 = tf.matmul(h2, w3) + b3

    # 4. 第四层：对h3的结果进行sigmoid转换(logistic回归)
    y_data = tf.nn.sigmoid(tf.slice(h3, [0, 0], [batch_size, -1]))
    y_generated = tf.nn.sigmoid(tf.slice(h3, [batch_size, 0], [-1, -1]))

    return y_data, y_generated, [w1, b1, w2, b2, w3, b3]


def show_result(x_gen_val, fname):
    """
    将图像保存到对应的文件(x_gen_val中的前64张图像转换为一张图像)
    :param x_gen_val:
    :param fname:
    :return:
    """
    x_gen_val = 0.5 * x_gen_val.reshape((x_gen_val.shape[0], image_height, image_weight)) + 0.5
    _, img_h, img_w = x_gen_val.shape
    grid_h = img_h * 8 + 5 * (8 - 1)
    grid_w = img_w * 8 + 5 * (8 - 1)
    img_grid = np.zeros((grid_h, grid_w), dtype=np.uint8)
    for i, res in enumerate(x_gen_val):
        if i >= 8 * 8:
            break
        img = (res) * 255
        img = img.astype(np.uint8)
        row = (i // 8) * (img_h + 5)
        col = (i % 8) * (img_w + 5)
        img_grid[row:row + img_h, col:col + img_w] = img
    imsave(fname, img_grid)


def train():
    """
    模型训练
    :return:
    """
    # 1. 加载数据(真实数据)
    mnist = input_data.read_data_sets('data/', one_hot=True)

    # 2. 网络的占位符(训练数据)变量定义
    x_data = tf.placeholder(tf.float32, [batch_size, image_size], name='x_data')
    z_prior = tf.placeholder(tf.float32, [batch_size, z_size], name='z_prior')
    keep_prob = tf.placeholder(tf.float32, name='keep_prob')
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # 3. 构建生成模型
    x_generated, g_params = build_generator(z_prior)

    # 4. 构建判别模型
    y_data, y_generated, d_params = build_disciminator(x_data, x_generated, keep_prob)

    # 5. 损失函数
    d_loss = -(tf.log(y_data) + tf.log(1 - y_generated))
    g_loss = -tf.log(y_generated)

    # 6. 定义优化函数
    optimizer = tf.train.AdamOptimizer(0.0001)
    # var_list: 表示给定更新那些参数
    d_trainer = optimizer.minimize(d_loss, var_list=d_params)
    g_trainer = optimizer.minimize(g_loss, var_list=g_params)

    # 7. 准备开始模型训练&模型的存储
    saver = tf.train.Saver()
    sess = tf.Session()
    # 初始化全局变量
    sess.run(tf.global_variables_initializer())

    # 判断一下是否是第一次训练&判断一下是否加载模型继续训练
    chkpt_fname = None
    if is_restore:
        # 加载模型继续训练
        chkpt_fname = tf.train.latest_checkpoint(checkpoint_dir)
        if chkpt_fname:
            print("load model......")
            saver.restore(sess, chkpt_fname)
    if not chkpt_fname:
        # 第一次训练&删除模型，重新训练；或者没有找到对应的模型保存位置
        print("Create model checkpoint dir.....")
        if os.path.exists(checkpoint_dir):
            shutil.rmtree(checkpoint_dir)
        os.mkdir(checkpoint_dir)

    # 产生全局的噪音数据，用于后面测试
    z_sample_val = np.random.normal(0, 1, size=(batch_size, z_size)).astype(np.float32)
    steps = int(10000 / batch_size)
    for i in range(sess.run(global_step), max_epoch):
        for j in range(steps):
            print("Epoch:{}, Steps:{}".format(i, j))
            # 获取batch_size个真实数据
            x_data_value, _ = mnist.train.next_batch(batch_size)
            x_data_value = 2 * x_data_value.astype(np.float32) - 1
            # 获取训练数据（噪音）
            z_value = np.random.normal(0, 1, size=[batch_size, z_size]).astype(np.float32)

            # 执行判断操作
            sess.run(d_trainer, feed_dict={x_data: x_data_value, z_prior: z_value, keep_prob: 0.7})
            # 执行生成的训练
            sess.run(g_trainer, feed_dict={x_data: x_data_value, z_prior: z_value, keep_prob: 0.7})

        # 输出一下一次迭代后的生成的相关信息
        x_gen_val = sess.run(x_generated, feed_dict={z_prior: z_sample_val})
        show_result(x_gen_val, "output_sample/random_sample{}.jpg".format(i))

        # 每完成一个迭代，将模型保存一下
        sess.run(tf.assign(global_step, i + 1))
        saver.save(sess, os.path.join(checkpoint_dir, 'model'), global_step=global_step)
    # 关闭会话
    sess.close()


def test():
    z_prior = tf.placeholder(tf.float32, [batch_size, z_size], name='z_prior')
    x_generated, _ = build_generator(z_prior)
    chkpt_fname = tf.train.latest_checkpoint(checkpoint_dir)
    sess = tf.Session()
    saver = tf.train.Saver()
    if chkpt_fname:
        print("load model......")
        saver.restore(sess, chkpt_fname)
    z_sample = np.random.normal(0, 1, size=(batch_size, z_size)).astype(np.float32)
    x_gen_val = sess.run(x_generated, feed_dict={z_prior: z_sample})
    show_result(x_gen_val, "output_sample/test.jpg")


if __name__ == '__main__':
    train()
    # test()
