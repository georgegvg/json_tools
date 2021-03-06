from json_tools import SECTIONSEP, walk_files
import argparse
import json
import os
import sys


def check_json_validity(path, args):
    try:
        with open(path) as f:
            json.load(f)
            return True
    except Exception as e:
        print(SECTIONSEP)
        print(f"Failed to load {path} {e}")
        return False


def check_validity(path, args):
    res = True
    for f in walk_files(path, r".*\.json"):
        f_res = check_json_validity(f, args)
        res = res and f_res
    return res


def main():
    parser = argparse.ArgumentParser(description='check validity of json files')
    parser.add_argument("file_path", metavar="FILE_OR_DIR_PATH", type=str,
                        help="Path to json file, or directory")
    args = parser.parse_args()
    if os.path.isdir(args.file_path):
        res = check_validity(args.file_path, args)
    else:
        res = check_json_validity(args.file_path, args)
    if not res:
        sys.exit("Some Json are broken")
