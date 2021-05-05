import boto3
import json
import yaml
import os
import common
import datetime

import database

def process_local(client, images):

    SERVICE = "aws"

    out = database.Database( "results2.db" )

    for imageFile in images:
        image = open(imageFile, "rb")
        content = image.read()
        response = client.detect_labels(
            Image={"Bytes": content}  # If MinConfidence is not specified,
            # the operation returns labels with a confidence values greater than or equal to 55 percent.
        )

        out.save_api_response( imageFile, SERVICE, response )


        for label_counter, label in enumerate(response["Labels"]):

            label_num = label_counter
            label_name = label["Name"]
            confidence = label["Confidence"]

            out.save_label( imageFile, SERVICE, label_name, label_num, confidence )


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
        process_local(client, images)
