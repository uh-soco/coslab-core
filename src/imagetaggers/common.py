import os
import imghdr

MIN_CONFIDENCE = 0.5


def arguments():

    import argparse

    parser = argparse.ArgumentParser(
        description="Automatically tag pictures using exernal APIs."
    )

    parser.add_argument("--config", type=str,
                        help="Path to the configuration file", required=True)

    ## todo: implement me

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="Path to file containing URLs")
    group.add_argument("--folder", type=str,
                       help="Path to folder containing images")

    parser.add_argument(
        "--output",
        default="./output/",
        type=str,
        help="Folder and file where results are stored.",
    )

    return parser.parse_args()


def load_config(file):

    import json
    import yaml

    print(file)

    if file.endswith('.yaml'):
        return yaml.safe_load(open(file))
    if file.endswith('.json'):
        return json.load(open(file))

    return {}


def image_files(folder):
    out = []
    for root, folders, files in os.walk(folder):
        files = map(lambda f: root + '/' + f, files)
        files = filter(lambda f: imghdr.what(f) != None, files)
        out += files
    return list(out)
