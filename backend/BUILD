py_library(
    name = "logging",
    srcs = ["logging.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "multiplexer",
    srcs = ["multiplexer.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_multiplexer",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:directory_watcher",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_accumulator", 
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:io_wrapper",
        "@org_pythonhosted_six",
        ":logging",
    ],
)

py_library(
    name = "application",
    srcs = ["application.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
        "@org_tensorflow_tensorboard//tensorboard/backend:application",
        ":multiplexer",
    ],
)

py_library(
    name = "program",
    srcs = ["program.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@org_tensorflow_tensorboard//tensorboard:program",
        "@org_tensorflow_tensorboard//tensorboard:version",
        ":application",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_file_inspector",
        "@org_pocoo_werkzeug",
        "@org_pythonhosted_six",
        ":logging",
    ],
)