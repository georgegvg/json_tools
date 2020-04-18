#!/usr/bin/python3

import json
import re
import concurrent.futures
from collections import defaultdict
import os
import argparse


class JsonPath(object):

    def __init__(self, t=tuple()):
        self.res = t

    def __add__(self, other):
        return JsonPath(self.res + (other,))

    def __str__(self):
        def get_type(s):
            if isinstance(s, int):
                return f"[{s}]"
            return f".{s}"

        if self.res:
            return str(self.res[0]) + ''.join(get_type(s) for s in self.res[1:])
        return ""

    def __hash__(self):
        return hash(self.res)

    def __lt__(self, other):
        return self.res < other.res


class _SearchResult(object):
    def __init__(self, pattern, verbose=True, match_path=True, title=""):
        self.matched_keys = {}
        self.matched_values = {}
        self.matched_paths = set()
        self.re = re.compile(pattern)
        self.verbose = verbose
        self.do_match_path = match_path
        self.pattern = pattern
        self.title = title

    @staticmethod
    def json_value_str(v):
        if isinstance(v, str):
            return f'"{v}"'
        return str(v)

    def _print(self, s):
        if self.verbose:
            print(s)

    def match_key(self, key, path):
        if self.re.match(str(key)):
            self._print(f"key {path} : {key}")
            self.matched_keys[path] = key

    def match_value(self, value, path):
        if self.re.match(str(value)):
            self._print(f"value {path}: {self.json_value_str(value)}")
            self.matched_values[path] = value

    def match_path(self, path):
        if self.do_match_path and self.re.match(str(path)):
            self._print(f"path {path}")
            self.matched_paths.add(path)

    def __str__(self):
        sectionsep = '-' * 40
        return os.linesep.join((
            sectionsep,
            self.title,
            sectionsep,
            os.linesep.join((
                sectionsep,
                "Matched Keys",
                sectionsep,
                os.linesep.join(f"{path} : {key}" for path, key in sorted(self.matched_keys.items())),
                sectionsep,
            )) if self.matched_keys else "",
            os.linesep.join((
                sectionsep,
                "Matched Values",
                sectionsep,
                os.linesep.join(f"{path}: {self.json_value_str(value)}" for path, value in
                                sorted(self.matched_values.items())),
                sectionsep,
            )) if self.matched_values else "",
            os.linesep.join((
                sectionsep,
                "Matched Paths",
                sectionsep,
                os.linesep.join(f"{path}" for path in sorted(self.matched_paths)),
                sectionsep,
            )) if self.matched_paths else "",
        ))


class Json(object):
    def __init__(self, j=None, file_path=None):
        self.title = "json"
        if file_path:
            self.title = file_path
            with open(file_path) as f:
                self.j = json.load(f)
        elif isinstance(j, str):
            self.title = f"json {j[:40]}..."
            self.j = json.loads(j)
        else:
            self.j = j
        self.cache = {}

    def _search(self, node, path, res):
        res.match_path(path)
        if isinstance(node, dict):
            for k, v in node.items():
                res.match_key(k, path)
                self._search(v, path + k, res)
        elif isinstance(node, list):
            for k, v in enumerate(node):
                self._search(v, path + k, res)
        else:
            res.match_value(node, path)

    def search(self, pattern, override_cache=False, verbose=True, match_path=False):
        if override_cache or pattern not in self.cache:
            self.cache[pattern] = res = _SearchResult(pattern,
                                                      verbose=verbose,
                                                      match_path=match_path,
                                                      title=self.title)
            self._search(self.j, JsonPath(), res)

        return self.cache[pattern]


def main():
    pass


if __name__ == "__main__":
    main()
