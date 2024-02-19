import os
import random

import gr_tensorboard
import tensorflow as tf
from gr_tensorboard.lib.config_writer import ParamPlotConfigWriter
from tensorboard.plugins.scalar import summary


def run(run_path, parameter_dict, values):
    tf.reset_default_graph()

    tag_value_placeholder = tf.placeholder(dtype=tf.float32, shape=())
    summary_op = summary.op("random_tag", tag_value_placeholder)

    writer = tf.summary.FileWriter(run_path)
    config_writer = ParamPlotConfigWriter(run_path)

    for parameter in parameter_dict:
        config_writer.AddParameter(parameter, parameter_dict[parameter])

    with tf.Session() as session:
        for value in values:
            summary_data = session.run(
                summary_op, feed_dict={tag_value_placeholder: value})
            writer.add_summary(summary_data)

    writer.close()
    config_writer.Save()


if __name__ == "__main__":
    logdir = os.path.join(os.path.dirname(__file__), 'scalarlogdir')

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    runs = ["1", "2", "3"]

    def runset1(run_names):
        return list(
            map(lambda x: os.path.join(logdir, 'runset1', x), run_names))

    def runset2(run_names):
        return list(
            map(lambda x: os.path.join(logdir, 'runset2', 'somedir', x),
                run_names))

    runpaths = runset1(runs) + runset2(runs)

    for run_path in runpaths:
        run(run_path, {"parameter": random.randint(1, 100)},
            [random.uniform(1, 100) for _ in range(random.randint(1, 12))])
