import json
import re
import concurrent.futures
from collections import defaultdict
import os
import argparse
import yaml


class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None


SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)


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
            return str(self.res[0]) + "".join(get_type(s) for s in self.res[1:])
        return ""

    def __hash__(self):
        return hash(self.res)

    def __lt__(self, other):
        return self.res < other.res

    def __len__(self):
        return len(self.res)


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

    def __bool__(self):
        if self.matched_keys or self.matched_values or self.matched_paths:
            return True
        return False

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
            self._print(f"key {path}.{key}" if path else f"{key}")
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
            os.linesep.join((
                "Matched Keys",
                sectionsep,
                os.linesep.join(f"{path}.{key}" if path else f"{key}"
                                for path, key in sorted(self.matched_keys.items())),
                sectionsep,
            )) if self.matched_keys else "",
            os.linesep.join((
                "Matched Values",
                sectionsep,
                os.linesep.join(f"{path}: {self.json_value_str(value)}"
                                for path, value in sorted(self.matched_values.items())),
                sectionsep,
            )) if self.matched_values else "",
            os.linesep.join((
                "Matched Paths",
                sectionsep,
                os.linesep.join(f"{path}" for path in sorted(self.matched_paths)),
                sectionsep,
            )) if self.matched_paths else "",
        ))


class JsonOrYaml(object):
    def __init__(self, j=None, file_path=None, try_load_inner_jsons=True):
        if file_path:
            self.title = file_path
            self.j = self._try_open_file(file_path, try_load_inner_jsons=try_load_inner_jsons)
        elif isinstance(j, str):
            self.title = f"json {j[:40]}..."
            self.j = json.loads(j)
        else:
            self.j = j
        self.cache = {}

    @classmethod
    def _try_open_file(cls, file_path, try_load_inner_jsons=True):
        j = cls._try_open_json(file_path)
        if not j:
            j = cls._try_open_yaml(file_path)
        if not j:
            raise TypeError(f"the specified file {file_path} is not Json or Yaml")
        if try_load_inner_jsons:
            return cls._try_load_inner_jsons(j)
        return j

    @classmethod
    def _try_load_inner_jsons(cls, node):
        if isinstance(node, dict):
            return {k: cls._try_load_inner_jsons(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [cls._try_load_inner_jsons(v) for v in node]
        elif isinstance(node, str):
            try:
                return json.loads(node)
            except Exception as _:
                return node
        return node

    @classmethod
    def _try_open_yaml(cls, file_path):
        try:
            with open(file_path) as f:
                y = [i for i in yaml.load_all(f, Loader=SafeLoaderIgnoreUnknown)]
                if len(y) == 1:
                    return y[0]
                else:
                    return y
        except Exception as e:
            raise e

    @staticmethod
    def _try_open_json(file_path):
        try:
            with open(file_path) as f:
                return json.load(f)
        except Exception as _:
            return None

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


def walk_searchable_files(path):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith('.yaml') or
                    file.endswith('.yml') or
                    file.endswith('.json')):
                yield os.path.join(subdir, file)


def search_file(path, args):
    joy = JsonOrYaml(file_path=path, try_load_inner_jsons=not args.disable_inner)
    s = joy.search(args.reg_exp, verbose=args.verbose)
    if s:
        print(s)


def search_dir(path, args):
    for f in walk_searchable_files(path):
        try:
            search_file(f, args)
        except Exception as _:
            pass


def main():
    parser = argparse.ArgumentParser(description='Search for regexps in Json or yaml')
    parser.add_argument("file_path", metavar="JSON_FILE_PATH", type=str, help="Path to json file")
    parser.add_argument("reg_exp", metavar="REG_EXP", type=str, help="Regular expression to search")
    parser.add_argument("--verbose", action="store_true", help="show results on the fly")
    parser.add_argument("--disable_inner", action="store_true", help="disable parsing inner json strings")
    args = parser.parse_args()
    if os.path.isdir(args.file_path):
        search_dir(args.file_path, args)
    else:
        search_file(args.file_path, args)
