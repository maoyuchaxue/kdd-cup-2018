# -*- coding: utf-8 -*-

import tensorflow as tf


LAMBDA = 1e-5
class AQModel:
    def __init__(self,
                 is_train,
                 aq_stations=10,
                 meo_stations=10,
                 learning_rate=0.001,
                 learning_rate_decay_factor=0.95,
                 aq_features=3,
                 prev_aq_features=12,
                 meo_features=25,
                 dist_features=4,
                 keep_prob=0.7):

        self.x_ = tf.placeholder(tf.float32, (None, meo_stations, meo_features)) # n * meo_n * meo_d
        self.prev_y_ = tf.placeholder(tf.float32, (None, aq_stations, prev_aq_features)) # n * aq_n * prev_aq_d
        self.y_ = tf.placeholder(tf.float32, (None, aq_stations, aq_features)) # n * aq_n * aq_d
        self.dist_mat = tf.placeholder(tf.float32, (aq_stations, meo_stations, dist_features)) # aq_n * meo_n * d
        self.keep_prob = keep_prob
        self.cur_batch_size = tf.placeholder(tf.int32)
        
        self.x_lin1 = tf.reshape(self.x_, [-1, meo_features])

        lin1 = tf.layers.dense(self.x_lin1, 128, use_bias=False,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        bn1 = tf.layers.batch_normalization(lin1, training=is_train)
        relu1 = tf.nn.relu(bn1)
        relu1_drop = tf.layers.dropout(relu1, 1 - self.keep_prob, training=is_train)

        lin2 = tf.layers.dense(relu1_drop, dist_features * 128, use_bias=False,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        bn2 = tf.layers.batch_normalization(lin2, training=is_train)
        relu2 = tf.nn.relu(bn2)

        relu2 = tf.reshape(relu2, [-1, meo_stations, dist_features, 128])
        relu2 = tf.transpose(relu2, (0, 3, 1, 2)) # n * 128 * meo_n * d
        relu2 = tf.reshape(relu2, [-1, meo_stations * dist_features])

        dist_m = tf.transpose(self.dist_mat, (1, 2, 0))
        dist_m = tf.reshape(dist_m, (-1, tf.shape(dist_m)[2]))

        lin3 = tf.matmul(relu2, dist_m) # 128n * aq_n
        lin3 = tf.reshape(lin3, (-1, 128, aq_stations))
        lin3 = tf.transpose(lin3, (0, 2, 1))

        lin4 = tf.layers.dense(lin3, 128, use_bias=True,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)

        bn4 = tf.layers.batch_normalization(lin4, training=is_train)
        relu4 = tf.nn.relu(bn4)
        relu4_drop = tf.layers.dropout(relu4, 1 - self.keep_prob, training=is_train)
        
        lin_prev1 = tf.layers.dense(self.prev_y_, 256, use_bias=True,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        bn_prev1 = tf.layers.batch_normalization(lin_prev1, training=is_train)
        relu_prev1 = tf.nn.relu(bn_prev1)
        relu_prev1_drop = tf.layers.dropout(relu_prev1, 1 - self.keep_prob, training=is_train)

        lin_prev2 = tf.layers.dense(relu_prev1_drop, 128, use_bias=True,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)

        bn_prev2 = tf.layers.batch_normalization(lin_prev2, training=is_train)
        relu_prev2 = tf.nn.relu(bn_prev2)
        relu_prev2_drop = tf.layers.dropout(relu_prev2, 1 - self.keep_prob, training=is_train)

        # new_shape = tf.concat([self.cur_batch_size, [aq_stations, 128]], 0)
        # relu_prev2_drop = tf.reshape(relu_prev2_drop, new_shape)
        # relu4_drop = tf.reshape(relu4_drop, new_shape)
        relu_prev2_drop = tf.reshape(relu_prev2_drop, (-1, aq_stations, 128))
        relu4_drop = tf.reshape(relu4_drop, (-1, aq_stations, 128))

        print(relu_prev2_drop, relu4_drop)
        concated = tf.concat([relu4_drop, relu_prev2_drop], 2)

        lin5 = tf.layers.dense(concated, aq_features, use_bias=True,
                kernel_regularizer=tf.contrib.layers.l2_regularizer(LAMBDA), activation=None)
        
        self.pred = lin5
        
        # self.loss = 2 * tf.reduce_mean(tf.abs(self.pred - self.y_) / (tf.abs(self.pred) + tf.abs(self.y_) + 1e-3))

        self.loss = tf.reduce_mean(tf.squared_difference(self.pred, self.y_))
        
        self.learning_rate = tf.Variable(float(learning_rate), trainable=False, dtype=tf.float32)
        self.learning_rate_decay_op = self.learning_rate.assign(self.learning_rate * learning_rate_decay_factor)  # Learning rate decay

        self.global_step = tf.Variable(0, trainable=False)
        self.params = tf.trainable_variables()

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            self.train_op = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.loss, global_step=self.global_step,var_list=self.params)  # Use Adam Optimizer

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



