# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Simple demo which writes a bunch of toy metrics to events file in various run directories for tensorboard to read"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import random

import tensorflow as tf
from tensorboard.plugins.scalar import summary
from lib.config_writer import ParamPlotConfigWriter

# Directory into which to write tensorboard data.
LOGDIR = '/tmp/paramplotdemo2'


def run(logdir, run_name, tag_value_map, parameter_map):
    """Create a dummy set of events data by logging some fake metrics to the runs directory."""

    tf.reset_default_graph()

    placeholders = {tag: tf.placeholder(shape=(), dtype=tf.float32) for tag in tag_value_map}
    summary_ops = {tag: summary.op(tag, placeholders[tag]) for tag in tag_value_map}

    run_path = os.path.join(logdir, run_name)
    writer = tf.summary.FileWriter(run_path)
    config_writer = ParamPlotConfigWriter(run_path)

    # Add the parameters to the run config
    config_writer.SetParameters(parameter_map)

    # Write the value under the final_loss summary for that particular run
    with tf.Session() as session:
        for tag_name in tag_value_map:
            for _ in range(tag_value_map[tag_name]["samples"]):
                summary_data = session.run(summary_ops[tag_name], feed_dict={placeholders[tag_name]: tag_value_map[tag_name]["func"]()})
                writer.add_summary(summary_data)

    config_writer.Save()
    writer.close()


def run_all(logdir, run_names, tag_value_maps, parameter_maps, unused_verbose=False):
    """Run the simulation for every logdir.
    """
    for run_name in run_names:
        run(logdir, run_name,
            tag_value_maps[run_name], parameter_maps[run_name])


def main(unused_argv):
    print('Saving output to %s.' % LOGDIR)

    def append_dir1(run_name):
        return os.path.join("runset1", run_name)
    
    def append_dir2(run_name):
        return os.path.join("runset2", run_name)
    
    run_prefix_funcs = [append_dir1, append_dir2]

    def create_run(index):
        return run_prefix_funcs[index % 2]("run"+str(index))

    int_parameters = [random.randint(1, 100) for _ in range(0, 5)]
    float_parameters = [random.uniform(0, 100) for _ in range(0, 5)]
    float2_parameters = [random.uniform(0, 100) for _ in range(0, 5)]
    float3_parameters = [random.uniform(0, 100) for _ in range(0, 5)]

    parameters = [(x, y, z, u) for x in int_parameters for y in float_parameters for z in float2_parameters for u in float3_parameters]
    runs = [create_run(index) for (index, _) in enumerate(parameters)]
    
    def create_metrics(index):
        return {
            "single-metric": {
                "samples": 1,
                "func": lambda: random.uniform(0, 12),        
            },
            "epoch-varying-metric": {
                "samples": 10000,
                "func": lambda: random.uniform(0, 12),           
            },
        }
    
    def create_parameters(int_param, float_param, float2_param, param2electricboogaloo):
        if random.uniform(0, 1) < 0.5: 
            return {
                "integer-parameter": int_param,
                "float-parameter": float_param,
                "super-secret-parameter": float2_param
            }
        else:
            return {
                "integer-parameter": int_param,
                "float-parameter": float_param,
                "super-secret-parameter": float2_param,
                "super-duper-secret-parameter": param2electricboogaloo
            }

    tag_value_maps = {runs[index]: create_metrics(index) for (index, _) in enumerate(parameters)}

    parameter_maps = {runs[index]: create_parameters(*params) for (index, params) in enumerate(parameters)}

    run_all(LOGDIR, runs, tag_value_maps, parameter_maps, unused_verbose=True)
    print('Done. Output saved to %s.' % LOGDIR)


if __name__ == '__main__':
    tf.app.run()
