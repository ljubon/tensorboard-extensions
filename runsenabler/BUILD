package(default_visibility = ["//visibility:public"])

load("@org_tensorflow_tensorboard//tensorboard/defs:web.bzl", "tf_web_library")

py_library(
    name = "runsenabler_loader",
    srcs = ["runsenabler_loader.py"],
    deps = [
        ":runsenabler_plugin",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
    ],
)

py_library(
    name = "runsenabler_plugin",
    srcs = ["runsenabler_plugin.py", "runsenabler_profiler.py"],
    deps = [
        "@org_pocoo_werkzeug",
        "@org_pythonhosted_six",
        "@org_tensorflow_tensorboard//tensorboard/backend:http_util",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_accumulator",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
        "//backend:io_helpers"
    ],
)

tf_web_library(
    name = "runsenabler_dashboard",
    srcs = ["runsenabler-dashboard.html"],
    path = "/runsenabler",
    visibility = ["//visibility:public"],
    deps = [
        "@org_tensorflow_tensorboard//tensorboard/components/tf_backend",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_color_scale",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_dashboard_common",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_imports:polymer",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_tensorboard:registry",
        "@org_polymer_paper_button",
        "@org_polymer_paper_spinner",
        "@org_polymer_paper_dialog",
        "@org_polymer_paper_styles",
    ],
)