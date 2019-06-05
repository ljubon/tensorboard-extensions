py_library(
    name = "logging",
    srcs = ["logging.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "application",
    srcs = ["application.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
        "@org_tensorflow_tensorboard//tensorboard/backend:application",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:io_wrapper",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_accumulator",
        ":io_helpers"
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

py_library(
    name = "io_helpers",
    srcs = ["io_helpers.py"],
    visibility = ["//visibility:public"],
)