gr_tensorboard/build_pip_package.sh &&
grtensorboard --logdir /tmp/paramplotdemo --max_reload_threads=4 --enable_profiling=True --default_runs_regex=^runset1/run\\d* --reload_interval=-1