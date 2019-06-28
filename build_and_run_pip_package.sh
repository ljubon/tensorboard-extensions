gr_tensorboard/build_pip_package.sh &&
grtensorboard --logdir /tmp/paramplotdemo --max_reload_threads=4 --enable_profiling --default_runs_regex="run[1][12][1234567]"