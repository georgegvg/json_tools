import re
import concurrent.futures
from collections import defaultdict
import os
import yaml

SECTIONSEP = '-' * 40


class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None


SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)


def walk_files(path, pattern):
    path_re = re.compile(pattern)
    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            if path_re.match(full_path):
                yield full_path
