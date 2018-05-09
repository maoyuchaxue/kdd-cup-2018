# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import os
import time

from mlp_model import Model
import dataset

import argparse
import sys, os
import math

parser = argparse.ArgumentParser(description="add arguments below:")
parser.add_argument('--test', action="store_false")
parser.add_argument('--name', type=str, help="test name", default="default")
parser.add_argument('--inf', type=int, help="inference version", default=2500)
arg = parser.parse_args()


summary_root = "./train/" + arg.name + "/"
if (not os.path.exists(summary_root)):
    os.mkdir(summary_root)

summary = "./train/" + arg.name + "/summary.log"

summary_file = None
if (not os.path.exists(summary)):
    summary_file = open(summary, "w")
else:
    summary_file = open(summary, "a")
    

tf.app.flags.DEFINE_integer("batch_size", 20, "batch size for training")
tf.app.flags.DEFINE_integer("num_epochs", 50, "number of epochs")
tf.app.flags.DEFINE_integer("valid_epochs", 5, "interval of validate epochs")
tf.app.flags.DEFINE_float("keep_prob", 0.7, "drop out rate")
tf.app.flags.DEFINE_boolean("is_train", arg.test, "False to inference")
tf.app.flags.DEFINE_string("data_dir", "", "data dir")
tf.app.flags.DEFINE_string("train_dir", "./train/" + arg.name, "training dir")
tf.app.flags.DEFINE_integer("inference_version", arg.inf, "the version for inferencing")
FLAGS = tf.app.flags.FLAGS
data = dataset.getDataset("beijing", "dayunit", batch_size=FLAGS.batch_size)


with tf.Session() as sess:
    if not os.path.exists(FLAGS.train_dir):
        os.mkdir(FLAGS.train_dir)
    
    if FLAGS.is_train:
        mlp_model = Model(True, batch_size=FLAGS.batch_size)
        if tf.train.get_checkpoint_state(FLAGS.train_dir):
            mlp_model.saver.restore(sess, tf.train.latest_checkpoint(FLAGS.train_dir))
        else:
            tf.global_variables_initializer().run()

        dist_mat = data.get_dist_matrix()

        for epoch in range(FLAGS.num_epochs):
            tot_train_losses = 0
            start_time = time.time()
            n_train = data.ns[0]
            iters = int(math.floor(n_train * 1.0 / FLAGS.batch_size))
            for i in range(iters):
                y_batch, X_batch = data.get_next_batch("train")
                print(X_batch.shape, y_batch.shape)
                feed = {mlp_model.x_: X_batch, mlp_model.y_: y_batch, mlp_model.keep_prob: FLAGS.keep_prob, mlp_model.dist_mat: dist_mat}

                cur_loss, _ = sess.run([mlp_model.loss, mlp_model.train_op], feed)

                print("iter: {iter_num}, batch loss {loss}".format(iter_num=i, loss=cur_loss))

                tot_train_losses += cur_loss
            # train_loss = train_epoch(mlp_model, sess, X_train, y_train)  # Complete the training process

            # val_acc, val_loss = valid_epoch(mlp_model, sess, X_val, y_val)  # Complete the valid process

            # if val_acc >= best_val_acc:  # when valid_accuracy > best_valid_accuracy, save the model
            #     best_val_acc = val_acc
            #     best_epoch = epoch + 1
            #     test_acc, test_loss = valid_epoch(mlp_model, sess, X_test, y_test)  # Complete the test process
                # mlp_model.saver.save(sess, '%s/checkpoint' % FLAGS.train_dir, global_step=mlp_model.global_step)

            epoch_time = time.time() - start_time
            train_loss = tot_train_losses / iters
            print("Epoch " + str(epoch + 1) + " of " + str(FLAGS.num_epochs) + " took " + str(epoch_time) + "s")
            print("  learning rate:                 " + str(mlp_model.learning_rate.eval()))
            print("  training loss:                 " + str(train_loss))
            # print("  validation loss:               " + str(val_loss))
            # print("  validation accuracy:           " + str(val_acc))
            # print("  best epoch:                    " + str(best_epoch))
            # print("  best validation accuracy:      " + str(best_val_acc))
            # print("  test loss:                     " + str(test_loss))
            # print("  test accuracy:                 " + str(test_acc))

            tup = (epoch+1, epoch_time, mlp_model.learning_rate.eval(), train_loss)
            summary_file.write(",".join([str(t) for t in tup]) + "\n")

            # if train_loss > max(pre_losses):  # Learning rate decay
            sess.run(mlp_model.learning_rate_decay_op)
            # pre_losses = pre_losses[1:] + [train_loss]

            if (epoch+1) % FLAGS.valid_epochs == 0:
                tot_valid_losses = 0
                start_time = time.time()
                n_valid = data.ns[1]
                iters = int(math.floor(n_valid * 1.0 / FLAGS.batch_size))
                for i in range(iters):
                    y_batch, X_batch = data.get_next_batch("val")
                    print(X_batch.shape, y_batch.shape)
                    feed = {mlp_model.x_: X_batch, mlp_model.y_: y_batch, mlp_model.keep_prob: FLAGS.keep_prob, mlp_model.dist_mat: dist_mat}
                    cur_loss, = sess.run([mlp_model.loss], feed)
                    tot_valid_losses += cur_loss
                val_loss = tot_valid_losses / iters
                print("validation: loss = " + str(val_loss))
