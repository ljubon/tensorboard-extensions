import argparse
import os
import signal
import sys
import threading
import base64
import json

from tensorboard import program
from tensorboard import version
from tensorboard.backend.event_processing import event_file_inspector as efi
from tensorboard.plugins import base_plugin

from .application import gr_tensorboard_wsgi
from .logging import get_logger

try:
  from absl import flags as absl_flags
  from absl.flags import argparse_flags
except ImportError:
  # Fall back to argparse with no absl flags integration.
  absl_flags = None
  argparse_flags = argparse

logger = get_logger()

def _cache_key(working_directory, arguments, configure_kwargs):
    """
    Code taken from the Tensorboard.manager module
    """
    if not isinstance(arguments, (list, tuple)):
      raise TypeError(
        "'arguments' should be a list of arguments, but found: %r "
        "(use `shlex.split` if given a string)"
        % (arguments,)
      )
    datum = {
        "working_directory": working_directory,
        "arguments": arguments,
        "configure_kwargs": configure_kwargs,
    }
    raw = base64.b64encode(
        json.dumps(datum, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    # `raw` is of type `bytes`, even though it only contains ASCII
    # characters; we want it to be `str` in both Python 2 and 3.
    return str(raw.decode("ascii"))


class GRTensorBoard(object):
  """Class for running the GR version of TensorBoard.
  Fields:
    plugin_loaders: Set from plugins passed to constructor.
    assets_zip_provider: Set by constructor.
    server_class: Set by constructor.
    flags: An argparse.Namespace set by the configure() method.
    cache_key: As `manager.cache_key`; set by the configure() method.
  """

  def __init__(self, plugins, assets_zip_provider):
    """Creates new instance.
    Args:
      plugins: A list of TensorBoard plugins to load, as TBLoader instances or
        TBPlugin classes.
      assets_zip_provider: Delegates to TBContext.

    :type plugins: list[Union[base_plugin.TBLoader, Type[base_plugin.TBPlugin]]]
    :type assets_zip_provider: () -> file
    """
    def make_loader(plugin):
      if isinstance(plugin, base_plugin.TBLoader):
        return plugin
      if issubclass(plugin, base_plugin.TBPlugin):
        return base_plugin.BasicLoader(plugin)
      raise ValueError("Not a TBLoader or TBPlugin subclass: %s" % plugin)
    
    self.plugin_loaders = [make_loader(p) for p in plugins]
    self.assets_zip_provider = assets_zip_provider
    self.server_class = program.WerkzeugServer
    self.flags = None

  def configure(self, argv=('',), **kwargs):
    """Configures TensorBoard behavior via flags.
    This method will populate the "flags" property with an argparse.Namespace
    representing flag values parsed from the provided argv list, overridden by
    explicit flags from remaining keyword arguments.
    Args:
      argv: Can be set to CLI args equivalent to sys.argv; the first arg is
        taken to be the name of the path being executed.
      kwargs: Additional arguments will override what was parsed from
        argv. They must be passed as Python data structures, e.g.
        `foo=1` rather than `foo="1"`.
    Returns:
      Either argv[:1] if argv was non-empty, or [''] otherwise, as a mechanism
      for absl.app.run() compatibility.
    Raises:
      ValueError: If flag values are invalid.
    """
    parser = argparse_flags.ArgumentParser(
        prog='tensorboard',
        description=('TensorBoard is a suite of web applications for '
                     'inspecting and understanding your TensorFlow runs '
                     'and graphs. https://github.com/tensorflow/tensorboard '))
    for loader in self.plugin_loaders:
      loader.define_flags(parser)
    arg0 = argv[0] if argv else ''
    flags = parser.parse_args(argv[1:])  # Strip binary name from argv.
    self.cache_key = _cache_key(
        working_directory=os.getcwd(),
        arguments=argv[1:],
        configure_kwargs=kwargs,
    )
    if absl_flags and arg0:
      # Only expose main module Abseil flags as TensorBoard native flags.
      # This is the same logic Abseil's ArgumentParser uses for determining
      # which Abseil flags to include in the short helpstring.
      for flag in set(absl_flags.FLAGS.get_key_flags_for_module(arg0)):
        if hasattr(flags, flag.name):
          raise ValueError('Conflicting Abseil flag: %s' % flag.name)
        setattr(flags, flag.name, flag.value)
    for k, v in kwargs.items():
      if not hasattr(flags, k):
        raise ValueError('Unknown TensorBoard flag: %s' % k)
      setattr(flags, k, v)
    for loader in self.plugin_loaders:
      loader.fix_flags(flags)
    self.flags = flags
    return [arg0]

  def main(self, ignored_argv=('',)):
    """Blocking main function for TensorBoard.
    This method is called by `tensorboard.main.run_main`, which is the
    standard entrypoint for the tensorboard command line program. The
    configure() method must be called first.
    Args:
      ignored_argv: Do not pass. Required for Abseil compatibility.
    Returns:
      Process exit code, i.e. 0 if successful or non-zero on failure. In
      practice, an exception will most likely be raised instead of
      returning non-zero.
    :rtype: int
    """
    self._install_signal_handler(signal.SIGTERM, "SIGTERM")
    if self.flags.inspect:
      logger.info('Not bringing up TensorBoard, but inspecting event files.')
      event_file = os.path.expanduser(self.flags.event_file)
      efi.inspect(self.flags.logdir, event_file, self.flags.tag)
      return 0
    try:
      server = self._make_server()
      sys.stderr.write('TensorBoard %s at %s (Press CTRL+C to quit)\n' %
                       (version.VERSION, server.get_url()))
      sys.stderr.flush()
      server.serve_forever()
      return 0
    except program.TensorBoardServerException as e:
      logger.error(e.msg)
      sys.stderr.write('ERROR: %s\n' % e.msg)
      sys.stderr.flush()
      return -1

  def launch(self):
    """Python API for launching TensorBoard.
    This method is the same as main() except it launches TensorBoard in
    a separate permanent thread. The configure() method must be called
    first.
    Returns:
      The URL of the TensorBoard web server.
    :rtype: str
    """
    # Make it easy to run TensorBoard inside other programs, e.g. Colab.
    server = self._make_server()
    thread = threading.Thread(target=server.serve_forever, name='TensorBoard')
    thread.daemon = True
    thread.start()
    return server.get_url()

  def _install_signal_handler(self, signal_number, signal_name):
    """Set a signal handler to gracefully exit on the given signal.
    When this process receives the given signal, it will run `atexit`
    handlers and then exit with `0`.
    Args:
      signal_number: The numeric code for the signal to handle, like
        `signal.SIGTERM`.
      signal_name: The human-readable signal name.
    """
    old_signal_handler = None  # set below
    def handler(handled_signal_number, frame):
      # In case we catch this signal again while running atexit
      # handlers, take the hint and actually die.
      signal.signal(signal_number, signal.SIG_DFL)
      sys.stderr.write("TensorBoard caught %s; exiting...\n" % signal_name)
      # The main thread is the only non-daemon thread, so it suffices to
      # exit hence.
      if old_signal_handler not in (signal.SIG_IGN, signal.SIG_DFL):
        old_signal_handler(handled_signal_number, frame)
      sys.exit(0)
    old_signal_handler = signal.signal(signal_number, handler)


  def _make_server(self):
    """Constructs the TensorBoard WSGI app and instantiates the server."""
    app = gr_tensorboard_wsgi(self.flags, self.plugin_loaders, self.assets_zip_provider)
    return self.server_class(app, self.flags)