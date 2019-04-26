rm -r /tmp/paramplotdemo &&
bazel run --incompatible_remove_native_http_archive=false //paramplot:paramplot_demo &&
python -m gr_tensorboard.main_deployed --logdir=/tmp/paramplotdemo
