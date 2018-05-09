# -*- coding: utf-8 -*-

import tensorflow as tf


LAMBDA = 1e-5
class Model:
    def __init__(self,
                 is_train,
                 batch_size=10,
                 learning_rate=0.01,
                 learning_rate_decay_factor=0.9,
                 aq_features=6,
                 meo_features=25,
                 dist_features=4):
        self.x_ = tf.placeholder(tf.float32, (batch_size, None, meo_features)) # n * meo_n * meo_d
        self.y_ = tf.placeholder(tf.float32, (batch_size, None, aq_features)) # n * aq_n * aq_d
        self.dist_mat = tf.placeholder(tf.float32, (None, None, dist_features)) # aq_n * meo_n * d
        self.keep_prob = tf.placeholder(tf.float32)
        
        self.x_lin1 = tf.reshape(self.x_, [-1, meo_features])

        lin1 = tf.layers.dense(self.x_lin1, 50, use_bias=False,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        bn1 = tf.layers.batch_normalization(lin1, training=is_train)
        relu1 = tf.nn.relu(bn1)
        relu1_drop = tf.nn.dropout(relu1, self.keep_prob)

        lin2 = tf.layers.dense(relu1_drop, dist_features * 20, use_bias=False,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        bn2 = tf.layers.batch_normalization(lin2, training=is_train)
        relu2 = tf.nn.relu(bn2)

        relu2 = tf.reshape(relu2, [batch_size, -1, dist_features, 20])
        relu2 = tf.transpose(relu2, (0, 3, 1, 2)) # n * 20 * meo_n * d
        relu2 = tf.reshape(relu2, [batch_size * 20, -1])

        dist_m = tf.transpose(self.dist_mat, (1, 2, 0))
        dist_m = tf.reshape(dist_m, (-1, tf.shape(dist_m)[2]))

        lin3 = tf.matmul(relu2, dist_m) # 20n * aq_n
        lin3 = tf.reshape(lin3, (batch_size, 20, -1))
        lin3 = tf.transpose(lin3, (0, 2, 1))

        lin4 = tf.layers.dense(lin3, 40, use_bias=True,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=tf.nn.relu)
        
        lin5 = tf.layers.dense(lin4, aq_features, use_bias=True,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        
        self.pred = lin5
        
        self.loss = tf.reduce_mean(tf.squared_difference(self.pred, self.y_))
        
        self.learning_rate = tf.Variable(float(learning_rate), trainable=False, dtype=tf.float32)
        self.learning_rate_decay_op = self.learning_rate.assign(self.learning_rate * learning_rate_decay_factor)  # Learning rate decay

        self.global_step = tf.Variable(0, trainable=False)
        self.params = tf.trainable_variables()

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            self.train_op = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss, global_step=self.global_step,var_list=self.params)  # Use Adam Optimizer

        self.saver = tf.train.Saver(tf.global_variables(), write_version=tf.train.SaverDef.V2,
                                    max_to_keep=3, pad_step_number=True, keep_checkpoint_every_n_hours=1.0)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def batch_normalization_layer(inputs, isTrain=True, is_conv_out=True, decay = 0.95):
    scale = tf.Variable(tf.ones([inputs.get_shape()[-1]]))
    beta = tf.Variable(tf.zeros([inputs.get_shape()[-1]]))
    pop_mean = tf.Variable(tf.zeros([inputs.get_shape()[-1]]), trainable=False)
    pop_var = tf.Variable(tf.ones([inputs.get_shape()[-1]]), trainable=False)

    if isTrain:
        if is_conv_out:
            batch_mean, batch_var = tf.nn.moments(inputs,[0,1,2])
        else:
            batch_mean, batch_var = tf.nn.moments(inputs,[0])   

        train_mean = tf.assign(pop_mean,
                               pop_mean * decay + batch_mean * (1 - decay))
        train_var = tf.assign(pop_var,
                              pop_var * decay + batch_var * (1 - decay))
        with tf.control_dependencies([train_mean, train_var]):
            return tf.nn.batch_normalization(inputs,
                batch_mean, batch_var, beta, scale, 0.00001)
    else:
        return tf.nn.batch_normalization(inputs,
            pop_mean, pop_var, beta, scale, 0.00001)



