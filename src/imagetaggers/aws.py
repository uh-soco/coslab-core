import json
import datetime

import boto3
from botocore.config import Config

from taggerresults import TaggerResults
import common


def _client(api_id="", api_key="", region=""):

    client = boto3.client(
        "rekognition",
        aws_access_key_id=api_id,
        aws_secret_access_key=api_key,
        region_name=region,
        config=Config(
            connect_timeout=5,
            read_timeout=60,
            retries={'max_attempts': 20}
            )
    )

    return client


def client(config):

    SERVICE = "aws"

    return _client(api_id=config[SERVICE]['api_id'], api_key=config[SERVICE]['api_key'], region=config[SERVICE]['api_region'])


def process_local(client, out, image_file, min_confidence=common.MIN_CONFIDENCE):

    SERVICE = "aws"

    image = open(image_file, 'rb')
    content = image.read()

    response = client.detect_labels(
        Image={"Bytes": content},
        MinConfidence=min_confidence
    )

    out.save_api_response(image_file, SERVICE, response)

    for label_counter, label in enumerate(response["Labels"]):

        label_num = label_counter
        label_name = label["Name"]
        confidence = float(label["Confidence"]) / 100

        out.save_label(image_file, SERVICE, label_name, label_num, confidence)
