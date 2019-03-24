""" Freeze variables and convert 2 generator networks to 2 GraphDef files.
This makes file size smaller and can be used for inference in production.
An example of command-line usage is:
python export_graph.py --dir saves \
                       --model dqn.pb\
                      
"""

import tensorflow as tf
import os
from tensorflow.python.tools.freeze_graph import freeze_graph
# from network import CycleGAN
from nn import H50AI, H50AI_TDlam
#import utils

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string('dir', 'saves', 'checkpoints directory path')
tf.flags.DEFINE_string('model', 'dqn.pb', 'model name, default: dqn.pb')
#tf.flags.DEFINE_string('YtoX_model', 'ink2real.pb', 'YtoX model name, default: ink2real.pb')
#tf.flags.DEFINE_integer('image_size', '512', 'image size, default: 256')

def export_graph(model_name):
  graph = tf.Graph()

  with graph.as_default():
    ai = H50AI_TDlam(stepsize=0.05, prob_factor=10, num_players=3)

    input_vec = tf.placeholder(tf.float32, [None, 3277], name='input_state')
    #output_vec = ai.session.run(ai.output,feed_dict={ai.input_state:input_vec,ai.stepsize_multiplier: 1, ai.stepsize_variable: 0.01})
    output_vec = ai.get_output(input_vec)
    output_vec = tf.identity(output_vec, name='output_prob')
    '''
    if XtoY:
      output_image = cycle_gan.G.sample(tf.expand_dims(input_image, 0))
    else:
      output_image = cycle_gan.F.sample(tf.expand_dims(input_image, 0))
    '''

    restore_saver = tf.train.Saver()
    export_saver = tf.train.Saver()

  with tf.Session(graph=graph) as sess:
    sess.run(tf.global_variables_initializer())
    latest_ckpt = tf.train.latest_checkpoint(FLAGS.dir)
    restore_saver.restore(sess, latest_ckpt)
    output_graph_def = tf.graph_util.convert_variables_to_constants(
        sess, graph.as_graph_def(), [output_vec.op.name])

    tf.train.write_graph(output_graph_def, 'pretrained', model_name, as_text=False)

def main(unused_argv):
  print('Export model...')
  export_graph(FLAGS.model)

if __name__ == '__main__':
  tf.app.run()
