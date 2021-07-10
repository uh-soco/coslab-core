import configparser
import os
import imghdr

config = configparser.ConfigParser()
config.read("config.ini")


def arguments():

    import argparse

    parser = argparse.ArgumentParser(
        description="Automatically tag pictures using exernal APIs."
    )
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument(
        "--secrets",
        type=str,
        default="./secrets.yaml",
        help="Path to the configuration file",
    )

    ## todo: implement me
    group.add_argument("--file", type=str, help="Path to file containing URLs")

    group.add_argument("--folder", type=str, help="Path to folder containing images")

    parser.add_argument(
        "--output",
        default="./output/",
        type=str,
        help="folder where the pictures will be stored",
    )

    return parser.parse_args()


def image_files( folder ):
    out = []
    for root, folders, files in os.walk( folder ):
        files = map( lambda f: root + '/' + f, files )
        files = filter( lambda f: imghdr.what( f ) != None, files )
        out += files
    return list( out )