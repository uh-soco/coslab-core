import configparser

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
