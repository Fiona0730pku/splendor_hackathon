"""Translate an image to another image
An example of command-line usage is:
python inference.py --model pretrained/ink2real.pb \
                       --input input_sample.jpg \
                       --output output_sample.jpg \
                       --image_size 256
"""

import tensorflow as tf
import sys
import os
#from network import CycleGAN
from nn import H50AI, H50AI_TDlam
#import utils
import numpy as np


def inference(input_vec, model_file='pretrained/dqn.pb'):
  graph = tf.Graph()

  with graph.as_default():
    input_vec1 = np.array(input_vec).reshape(-1, 3277).astype(np.float32)
    with tf.gfile.FastGFile(model_file, 'rb') as model_file1:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(model_file1.read())

    for node in graph_def.node:
      if node.op == 'RefSwitch':
        node.op = 'Switch'
        for index in range(len(node.input)):
          if 'moving_' in node.input[index]:
            node.input[index] = node.input[index] + '/read'
      elif node.op == 'AssignSub':
        node.op = 'Sub'
        if 'use_locking' in node.attr: del node.attr['use_locking']

    [output_vec] = tf.import_graph_def(graph_def,
                          input_map={'input_state': input_vec1},
                          return_elements=['output_prob:0'],
                          name='output')

  with tf.Session(graph=graph) as sess:
    generated = output_vec.eval()
    #print(generated)
    return generated
    #with open(FLAGS.output, 'wb') as f:
      #f.write(generated)


if __name__ == '__main__':
  tf.app.run()
