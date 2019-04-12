workspace(name = "io_github_tensorflow_tensorboard_plugin_example")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name = "build_bazel_rules_nodejs",
    sha256 = "3a3efbf223f6de733475602844ad3a8faa02abda25ab8cfe1d1ed0db134887cf",
    urls = ["https://github.com/bazelbuild/rules_nodejs/releases/download/0.27.12/rules_nodejs-0.27.12.tar.gz"],
)

load("@build_bazel_rules_nodejs//:defs.bzl", "node_repositories")

node_repositories(package_json = ["//:package.json"])

load("@build_bazel_rules_nodejs//:defs.bzl", "npm_install")

npm_install(
    name = "npm",
    package_json = "//:package.json",
    package_lock_json = "//:package-lock.json",
)

################################################################################
# CLOSURE RULES - Build rules and libraries for JavaScript development
#
# NOTE: SHA should match what's in TensorBoard's WORKSPACE file.
# NOTE: All the projects depended upon in this file use highly
#       available redundant URLs. They are strongly recommended because
#       they hedge against GitHub outages and allow Bazel's downloader
#       to guarantee high performance and 99.9% reliability. That means
#       practically zero build flakes on CI systems, without needing to
#       configure an HTTP_PROXY.

http_archive(
    name = "io_bazel_rules_closure",
    sha256 = "b29a8bc2cb10513c864cb1084d6f38613ef14a143797cea0af0f91cd385f5e8c",
    strip_prefix = "rules_closure-0.8.0",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_closure/archive/0.8.0.tar.gz",
        "https://github.com/bazelbuild/rules_closure/archive/0.8.0.tar.gz",  # 2018-08-03
    ],
)

load("@io_bazel_rules_closure//closure:defs.bzl", "closure_repositories")

# Inherit external repositories defined by Closure Rules.
closure_repositories(
    omit_com_google_protobuf = True,
    omit_com_google_protobuf_js = True,
)

################################################################################


http_archive(
    name = "ai_google_pair_facets",
    sha256 = "e3f7b7b3c194c1772d16bdc8b348716c0da59a51daa03ef4503cf06c073caafc",
    strip_prefix = "facets-0.2.1",
    urls = [
        "http://mirror.bazel.build/github.com/pair-code/facets/archive/0.2.1.tar.gz",
        "https://github.com/pair-code/facets/archive/0.2.1.tar.gz",
    ],
)

http_archive(
    name = "org_tensorflow",
    sha256 = "88324ad9379eae4fdb2aefb8e0d6c7cd0dc748b44daa5cc96ffd9415705c00c3",
    strip_prefix = "tensorflow-9752b117ff63f204c4975cad52b5aab5c1f5e9a9",
    urls = [
        "https://mirror.bazel.build/github.com/tensorflow/tensorflow/archive/9752b117ff63f204c4975cad52b5aab5c1f5e9a9.tar.gz",  # 2018-04-16
        "https://github.com/tensorflow/tensorflow/archive/9752b117ff63f204c4975cad52b5aab5c1f5e9a9.tar.gz",
    ],
)

load("@org_tensorflow//tensorflow:workspace.bzl", "tf_workspace")

tf_workspace()

http_archive(
    name = "org_tensorflow_tensorboard",
    sha256 = "e263f1ebeadaef246ebbd6d81faa02292ecf0193e5f0ecd279ee38416f2be4b3",
    strip_prefix = "tensorboard-1.12.0",
    urls = [
        "http://mirror.bazel.build/github.com/tensorflow/tensorboard/archive/1.12.0.tar.gz",
        "https://github.com/tensorflow/tensorboard/archive/1.12.0.tar.gz",
    ],
)

load("@org_tensorflow_tensorboard//third_party:workspace.bzl", "tensorboard_workspace")

# Inherit external repositories defined by Closure Rules.
tensorboard_workspace()
