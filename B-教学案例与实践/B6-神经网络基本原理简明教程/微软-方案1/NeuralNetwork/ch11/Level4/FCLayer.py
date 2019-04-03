# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import numpy as np

from Level4.Layer import *
from Level4.Activators import *
from Level4.WeightsBias import *
from Level4.Parameters import *

class FcLayer(CLayer):
    def __init__(self, input_size, output_size, activator):
        self.input_size = input_size
        self.output_size = output_size
        self.activator = activator

    def Initialize(self, param):
        self.weights = WeightsBias(self.input_size, self.output_size, param.init_method, param.optimizer_name, param.eta)
        self.weights.InitializeWeights()

    def forward(self, input):
        self.input_shape = input.shape
        if input.ndim == 3: # come from pooling layer
            self.x = input.reshape(input.size, 1)
        else:
            self.x = input
        self.z = np.dot(self.weights.W, self.x) + self.weights.B
        self.a = self.activator.forward(self.z)
        return self.a

    # 把激活函数算做是当前层，上一层的误差传入后，先经过激活函数的导数，而得到本层的针对z值的误差
    def backward(self, delta_in, flag):
        if flag == LayerIndexFlags.LastLayer or flag == LayerIndexFlags.SingleLayer:
            dZ = delta_in
        else:
            #dZ = delta_in * self.activator.backward(self.a)
            dZ,_ = self.activator.backward(self.z, self.a, delta_in)

        self.weights.dW = np.dot(dZ, self.x.T)
        self.weights.dB = np.sum(dZ, axis=1, keepdims=True)
        # calculate delta_out for lower level
        delta_out = np.dot(self.weights.W.T, dZ)

        if len(self.input_shape) > 2:
            return delta_out.reshape(self.input_shape)
        else:
            return delta_out

    def pre_update(self):
        self.weights.pre_Update()

    def update(self):
        self.weights.Update()
        
    def save_parameters(self, name):
        np.save(name+"_w", self.weights.W)
        np.save(name+"_b", self.weights.B)

    def load_parameters(self, name):
        self.weights.W = np.load(name+"_w.npy")
        self.weights.B = np.load(name+"_b.npy")
