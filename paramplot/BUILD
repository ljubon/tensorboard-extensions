package(default_visibility = ["//visibility:public"])

load("@org_tensorflow_tensorboard//tensorboard/defs:web.bzl", "tf_web_library")

licenses(["notice"])  # Apache 2.0

py_library(
    name = "paramplot_loader",
    srcs = ["paramplot_loader.py"],
    srcs_version = "PY2AND3",
    deps = [
        ":paramplot_plugin",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
    ],
)

py_library(
    name = "paramplot_plugin",
    srcs = ["paramplot_plugin.py"],
    srcs_version = "PY2AND3",
    deps = [
        "@org_pocoo_werkzeug",
        "@org_pythonhosted_six",
        "@org_tensorflow_tensorboard//tensorboard/backend:http_util",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_accumulator",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
    ],
)

py_binary(
    name = "paramplot_demo",
    srcs = ["paramplot_demo.py"],
    srcs_version = "PY2AND3",
    deps = [":paramplot_summary"],
)

py_library(
    name = "paramplot_summary",
    srcs = ["paramplot_summary.py"],
    srcs_version = "PY2AND3",
)

tf_web_library(
    name = "paramplot_dashboard",
    srcs = [
        "paramplot-dashboard.html",
    ],
    path = "/paramplot",
    deps = [
        ":paramplot_card",
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

tf_web_library(
    name = "paramplot_card",
    srcs = [
        "paramplot-card.html",
    ],
    path = "/paramplot",
    deps = [
        "@org_tensorflow_tensorboard//tensorboard/components/tf_backend",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_card_heading",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_color_scale",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_dashboard_common",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_imports:polymer",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_line_chart_data_loader",
        "//lib:simple_chart",
        "@org_polymer_paper_dropdown_menu",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_item",
        "@org_polymer_paper_listbox",
        "@org_polymer_paper_menu",
        "@org_polymer_paper_menu_button",
    ],
)
