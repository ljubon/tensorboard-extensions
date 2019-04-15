package(default_visibility = ["//visibility:public"])

load("@org_tensorflow_tensorboard//tensorboard/defs:web.bzl", "tf_web_library")

py_library(
    name = "runsenabler_loader",
    srcs = ["runsenabler_loader.py"],
    srcs_version = "PY2AND3",
    deps = [
        ":runsenabler_plugin",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
    ],
)

py_library(
    name = "runsenabler_plugin",
    srcs = ["runsenabler_plugin.py"],
    srcs_version = "PY2AND3",
    deps = [
        "@org_pocoo_werkzeug",
        "@org_pythonhosted_six",
        "@org_tensorflow_tensorboard//tensorboard/backend:http_util",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_accumulator",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
    ],
)

tf_web_library(
    name = "runsenabler_dashboard",
    srcs = [
        "runsenabler-dashboard.html",
    ],
    path = "/runsenabler",
    deps = [
        "@org_tensorflow_tensorboard//tensorboard/components/tf_backend",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_categorization_utils",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_color_scale",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_dashboard_common",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_data_selector:type",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_imports:lodash",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_imports:polymer",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_paginated_view",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_runs_selector",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_storage",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_tensorboard:registry",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_utils",
        "@org_tensorflow_tensorboard//tensorboard/components/vz_chart_helpers",
        "@org_polymer_iron_collapse",
        "@org_polymer_paper_button",
        "@org_polymer_paper_checkbox",
        "@org_polymer_paper_dropdown_menu",
        "@org_polymer_paper_input",
        "@org_polymer_paper_item",
        "@org_polymer_paper_menu",
        "@org_polymer_paper_slider",
        "@org_polymer_paper_styles",
    ],
)