package(default_visibility = ["//visibility:public"])

load("@org_tensorflow_tensorboard//tensorboard/defs:web.bzl", "tf_web_library")

filegroup(
    name = "node_modules",
    srcs = glob([
        "node_modules/**/*.js",
        "node_modules/**/*.d.ts",
        "node_modules/**/*.json",
    ]),
    visibility = ["//visibility:public"],
)

tf_web_library(
    name = "simple_chart",
    srcs = [
        "simple-chart.html",
        "simple-chart.ts",
    ],
    path = "/lib",
    deps = [
        ":node_modules",
    ]
)