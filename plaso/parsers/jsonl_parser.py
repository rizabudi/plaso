# -*- coding: utf-8 -*-
"""Base parser for line-based JSON (JSON-L) log formats."""

import json

from json import decoder as json_decoder

from dfvfs.helpers import text_file

from plaso.lib import errors
from plaso.parsers import interface
from plaso.parsers import manager


class JSONLParser(interface.FileObjectParser):
  """Base parser for line-based JSON (JSON-L) log formats."""

  NAME = 'jsonl'
  DATA_FORMAT = 'JSON-L log file'

  _ENCODING = 'utf-8'

  _MAXIMUM_LINE_LENGTH = 64 * 1024

  _plugin_classes = {}

  def ParseFileObject(self, parser_mediator, file_object):
    """Parses a line-based JSON (JSON-L) log file-like object.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      file_object (dfvfs.FileIO): a file-like object.

    Raises:
      WrongParser: when the file cannot be parsed.
    """
    encoding = self._ENCODING or parser_mediator.codepage

    # Use strict encoding error handling in the verification step so that
    # a JSON-L parser does not generate extraction warning for encoding errors
    # of unsupported files.
    text_file_object = text_file.TextFile(file_object, encoding=encoding)

    try:
      line = text_file_object.readline(size=self._MAXIMUM_LINE_LENGTH)
    except UnicodeDecodeError:
      raise errors.WrongParser('Not a JSON-L file or encoding not supported.')

    if not line:
      raise errors.WrongParser('Not a JSON-L file.')

    line = line.strip()
    if line[0] != '{' and line[-1] != '}':
      raise errors.WrongParser(
          'Not a JSON-L file, missing opening and closing braces.')

    try:
      json_dict = json.loads(line)
    except json_decoder.JSONDecodeError:
      raise errors.WrongParser('Not a JSON-L file, unable to decode JSON.')

    if not json_dict:
      raise errors.WrongParser('Not a JSON-L file, missing JSON.')

    for plugin in self._plugins:
      if parser_mediator.abort:
        break

      if plugin.CheckRequiredFormat(json_dict):
        plugin.Process(parser_mediator, file_object=file_object)


manager.ParsersManager.RegisterParser(JSONLParser)