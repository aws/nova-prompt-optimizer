# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import logging.config
import sys

LOGGING_LINE_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
LOGGING_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"


class NovaPromptOptimizerLoggingStream:
    """
    A Python stream for use with event logging APIs throughout NovaPromptOptimizer (`eprint()`,
    `logger.info()`, etc.). This stream wraps `sys.stderr`, forwarding `write()` and
    `flush()` calls to the stream referred to by `sys.stderr` at the time of the call.
    It also provides capabilities for disabling the stream to silence event logs.
    """

    def __init__(self):
        self._enabled = True

    def write(self, text):
        if self._enabled:
            sys.stderr.write(text)

    def flush(self):
        if self._enabled:
            sys.stderr.flush()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value


NOVA_PO_LOGGING_STREAM = NovaPromptOptimizerLoggingStream()


def disable_logging():
    """
    Disables the `NovaPromptOptimizerLoggingStream` used by event logging APIs throughout NovaPromptOptimizer
    (`eprint()`, `logger.info()`, etc), silencing all subsequent event logs.
    """
    NOVA_PO_LOGGING_STREAM.enabled = False


def enable_logging():
    """
    Enables the `NovaPromptOptimizerLoggingStream` used by event logging APIs throughout NovaPromptOptimizer
    (`eprint()`, `logger.info()`, etc), emitting all subsequent event logs. This
    reverses the effects of `disable_logging()`.
    """
    NOVA_PO_LOGGING_STREAM.enabled = True


def configure_nova_po_loggers(root_module_name):
    formatter = logging.Formatter(fmt=LOGGING_LINE_FORMAT, datefmt=LOGGING_DATETIME_FORMAT)

    nova_po_handler_name = "nova_po_handler"
    handler = logging.StreamHandler(stream=NOVA_PO_LOGGING_STREAM)
    handler.setFormatter(formatter)
    handler.set_name(nova_po_handler_name)

    logger = logging.getLogger(root_module_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for existing_handler in logger.handlers[:]:
        if getattr(existing_handler, "name", None) == nova_po_handler_name:
            logger.removeHandler(existing_handler)

    logger.addHandler(handler)