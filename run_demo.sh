rm -r /tmp/paramplotdemo &&
bazel run --incompatible_remove_native_http_archive=false //paramplot:paramplot_demo &&
bazel run --incompatible_remove_native_http_archive=false --incompatible_package_name_is_a_function=false :gr_tensorboard -- --logdir=/tmp/paramplotdemo