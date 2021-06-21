import boto3
import json
import yaml
import os
import common
import datetime

import output

def process_local(client, images, min_confidence = float( common.config["DEFAULT"]["minimal_confidence"] )):

    SERVICE = "aws"

    out = output.Output()

    for imageFile in images:
        image = open(imageFile, "rb")
        content = image.read()
        response = client.detect_labels(
            Image={"Bytes": content},
            MinConfidence=min_confidence
        )

        out.save_api_response(imageFile, SERVICE, response)

        for label_counter, label in enumerate(response["Labels"]):

            label_num = label_counter
            label_name = label["Name"]
            confidence = label["Confidence"]

            out.save_label(imageFile, SERVICE, label_name, label_num, confidence)

    return out


if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    secrets = yaml.safe_load(open(args.secrets))

    api_id = secrets["aws"]["api_id"]
    api_key = secrets["aws"]["api_key"]
    api_region = secrets["aws"]["api_region"]

    client = boto3.client(
        "rekognition",
        aws_access_key_id=api_id,
        aws_secret_access_key=api_key,
        region_name=api_region,
    )

    if args.folder:
        directory = args.folder
        images = [os.path.join(directory, file) for file in os.listdir(directory)]
        out = process_local(client, images)
        out.save_sql("aws.db")
