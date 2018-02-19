import os
import sys
import math
import numpy as np
import tensorflow as tf
import lib.network as network
import lib.naive_grid as naive_grid





class GRU_GRID_2:
    def __init__(self, n_cells=4, n_input=1024, n_hidden_state=256):
        self.W_u = naive_grid.weight_grid(
            'u', n_cells, n_input, n_hidden_state)
        self.W_r = naive_grid.weight_grid(
            'r', n_cells, n_input, n_hidden_state)
        self.W_h = naive_grid.weight_grid(
            'h', n_cells, n_input, n_hidden_state)

        self.b_u = naive_grid.bias_grid('u', n_cells, n_hidden_state)
        self.b_r = naive_grid.bias_grid('r', n_cells, n_hidden_state)
        self.b_h = naive_grid.bias_grid('h', n_cells, n_hidden_state)

        self.U_u = tf.Variable(tf.random_normal(
            [3, 3, 3, n_hidden_state, n_hidden_state]), name="U_u")
        self.U_r = tf.Variable(tf.random_normal(
            [3, 3, 3, n_hidden_state, n_hidden_state]), name="U_r")
        self.U_h = tf.Variable(tf.random_normal(
            [3, 3, 3, n_hidden_state, n_hidden_state]), name="U_h")

    def call(self, fc_input, prev_state):
        def linear(x, W, U, h, b):
            Wx = naive_grid.weight_grid_multiply(x, W)
            Uh = tf.nn.conv3d(h, U, strides=[1, 1, 1, 1, 1], padding="SAME")
            b = tf.convert_to_tensor(b)
            print(Wx.shape, Uh.shape, b.shape)
            return Wx + Uh + b

        u_t = tf.sigmoid(
            linear(fc_input, self.W_u, self.U_u, prev_state, self.b_u))
        r_t = tf.sigmoid(
            linear(fc_input, self.W_r, self.U_r, prev_state,  self.b_r))
        h_t = tf.multiply(1 - u_t, prev_state) + tf.multiply(u_t, tf.tanh(
            linear(fc_input, self.W_h, self.U_h, tf.multiply(r_t, prev_state), self.b_h)))

        return h_t


class LSTM_GRID:
    def __init__(self, batch_size):
        state_shape = [4, 4, 4, batch_size, 256]
        self.state = tf.contrib.rnn.LSTMStateTuple(
            tf.fill(state_shape, tf.to_float(0)), tf.fill(state_shape, tf.to_float(0)))
        self.W_f = tf.Variable(tf.ones([4, 4, 4, 1024, 256]), name="W_f")
        self.W_i = tf.Variable(tf.ones([4, 4, 4, 1024, 256]), name="W_i")
        self.W_o = tf.Variable(tf.ones([4, 4, 4, 1024, 256]), name="W_o")
        self.W_c = tf.Variable(tf.ones([4, 4, 4, 1024, 256]), name="W_c")

        self.U_f = tf.Variable(tf.ones([3, 3, 3, 256, 256]), name="U_f")
        self.U_i = tf.Variable(tf.ones([3, 3, 3, 256, 256]), name="U_i")
        self.U_o = tf.Variable(tf.ones([3, 3, 3, 256, 256]), name="U_o")
        self.U_c = tf.Variable(tf.ones([3, 3, 3, 256, 256]), name="U_c")

        self.b_f = tf.Variable(tf.ones([4, 4, 4, 1, 256]), name="b_f")
        self.b_i = tf.Variable(tf.ones([4, 4, 4, 1, 256]), name="b_i")
        self.b_o = tf.Variable(tf.ones([4, 4, 4, 1, 256]), name="b_o")
        self.b_c = tf.Variable(tf.ones([4, 4, 4, 1, 256]), name="b_c")

    def call(self, fc_input, prev_state_tuple):
        def linear(x, W, U, b):
            hidden_state, _ = prev_state_tuple
            Wx = tf.matmul(x, W)
            Uh = tf.nn.conv3d(hidden_state, U, strides=[
                1, 1, 1, 1, 1], padding="SAME")
            print(Wx.shape, Uh.shape, b.shape)
            return Wx + Uh + b

        _, prev_output = prev_state_tuple
        f_t = tf.sigmoid(linear(fc_input, self.W_f, self.U_f, self.b_f))
        i_t = tf.sigmoid(linear(fc_input, self.W_i, self.U_i, self.b_i))
        o_t = tf.sigmoid(linear(fc_input, self.W_o, self.U_o, self.b_o))
        c_t = tf.multiply(f_t, prev_output) + tf.multiply(i_t,
                                                          tf.tanh(linear(fc_input, self.W_c, self.U_c, self.b_c)))
        h_t = tf.multiply(o_t, tf.tanh(c_t))

        return h_t, tf.contrib.rnn.LSTMStateTuple(c_t, h_t)
