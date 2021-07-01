import boto3
import json
import yaml
import os
import common
import datetime

import output

def client(api_id, api_key, api_region):

    client = boto3.client(
        "rekognition",
        aws_access_key_id=api_id,
        aws_secret_access_key=api_key,
        region_name=api_region,
    )

    return client


def process_local(client, out, image_file, min_confidence = float( common.config["DEFAULT"]["minimal_confidence"] )):

    SERVICE = "aws"

    image = open(image_file, "rb")
    content = image.read()
    response = client.detect_labels(
        Image={"Bytes": content},
        MinConfidence=min_confidence
    )
    now = datetime.datetime.now()

    out.save_api_response(image_file, SERVICE, response, now )

    for label_counter, label in enumerate(response["Labels"]):

        label_num = label_counter
        label_name = label["Name"]
        confidence = label["Confidence"]

        out.save_label(image_file, SERVICE, label_name, label_num, confidence, now )


if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    secrets = yaml.safe_load(open(args.secrets))

    from progress.bar import Bar

    api_id = secrets["aws"]["api_id"]
    api_key = secrets["aws"]["api_key"]
    api_region = secrets["aws"]["api_region"]

    client = boto3.client(
        "rekognition",
        aws_access_key_id=api_id,
        aws_secret_access_key=api_key,
        region_name=api_region,
    )

    out = output.Output()

    if args.folder:
        directory = args.folder
        images = common.image_files( directory )

        bar = Bar('Images labelled', max = len(images) )

        for image in images:
            process_local(client, out, image)
            bar.next()

        bar.finish()

        out.export_sql("aws.db")
        out.export_pickle("aws.pickle")
