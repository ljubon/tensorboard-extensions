package(default_visibility = ["//visibility:public"])

load("@org_tensorflow_tensorboard//tensorboard/defs:web.bzl", "tf_web_library")

py_library(
    name = "paramplot_plugin",
    srcs = ["paramplot_plugin.py"],
    deps = [
        "@org_pythonhosted_six",
        "@org_tensorflow_tensorboard//tensorboard/backend:http_util",
        "@org_tensorflow_tensorboard//tensorboard/backend/event_processing:event_accumulator",
        "@org_tensorflow_tensorboard//tensorboard/plugins:base_plugin",
    ],
)

py_binary(
    name = "paramplot_demo",
    srcs = ["paramplot_demo.py"],
    deps = [":paramplot_summary", "//lib:config_writer"],
)

py_library(
    name = "paramplot_summary",
    srcs = ["paramplot_summary.py"],
)

tf_web_library(
    name = "paramplot_dashboard",
    srcs = [
        "paramplot-dashboard.html",
        "paramplot-card.html",
        "paramplot-helpers.html",
        "paramplot-helpers.ts"
    ],
    path = "/paramplot",
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
        "@org_tensorflow_tensorboard//tensorboard/components/tf_card_heading",
        "@org_tensorflow_tensorboard//tensorboard/components/tf_line_chart_data_loader",
        "@org_polymer_iron_collapse",
        "@org_polymer_paper_button",
        "@org_polymer_paper_checkbox",
        "@org_polymer_paper_dropdown_menu",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_input",
        "@org_polymer_paper_listbox",
        "@org_polymer_paper_item",
        "@org_polymer_paper_menu",
        "@org_polymer_paper_slider",
        "@org_polymer_paper_styles",
        "@org_polymer_paper_menu_button",
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
        "@org_polymer_paper_dropdown_menu",
        "@org_polymer_paper_icon_button",
        "@org_polymer_paper_item",
        "@org_polymer_paper_listbox",
        "@org_polymer_paper_menu",
        "@org_polymer_paper_menu_button",
    ],
)
