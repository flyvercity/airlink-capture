# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''Airlink Capture Tool Utility Functions.'''
import json
import logging as lg

from pygments import highlight
from pygments.lexers.jsonnet import JsonnetLexer
from pygments.formatters import TerminalFormatter


def pprint(data):
    '''Pretty print json with colors.

    Args:
        data: json data to print
    '''
    if lg.root.level == lg.DEBUG:
        json_str = json.dumps(data, indent=4, sort_keys=True)
        print(highlight(json_str, JsonnetLexer(), TerminalFormatter()))
