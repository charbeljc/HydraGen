from __future__ import annotations
from logzero import logger
from collections import abc
from orderedset import OrderedSet
import typing
import sys
class Config:
    _vetted: OrderedSet
    def __init__(self):
        self._vetted = OrderedSet()

    def ban(self, item: str):
        self._vetted.add(item)
        return self

    def is_banned(self, name):
        return name in self._vetted



