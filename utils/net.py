'''
Author: your name
Date: 2020-12-16 11:37:27
LastEditTime: 2020-12-16 11:45:22
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/focusDetect/utils/net.py
'''

import numpy as np
 
def sigmoid(x):
  # Our activation function: f(x) = 1 / (1 + e^(-x))
  return 1 / (1 + np.exp(-x))
 
class Neuron:
  def __init__(self, weights, bias):
    self.weights = weights
    self.bias = bias
 
  def feedforward(self, inputs):
    # Weight inputs, add bias, then use the activation function
    total = np.dot(self.weights, inputs) + self.bias
    return sigmoid(total)
 
weights = np.array([0, 1]) # w1 = 0, w2 = 1
bias = 0                   # b = 4
n = Neuron(weights, bias)
 
x = np.array([2, 3])       # x1 = 2, x2 = 3
print(n.feedforward(x))    # 0.9990889488055994