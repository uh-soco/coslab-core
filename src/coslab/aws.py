import json
import datetime

import boto3
from botocore.config import Config

from .taggerresults import TaggerResults
from .common import *

class AWS:

    SERVICE = "aws"

    def __init__(self, api_id="", api_key="", api_region=""):
        self.client = boto3.client(
            "rekognition",
            aws_access_key_id=api_id,
            aws_secret_access_key=api_key,
            region_name=api_region,
            config=Config(
                connect_timeout=5,
                read_timeout=60,
                retries={
                    'max_attempts': 5,
                    'mode': 'standard'
                    }
                )
        )

    @classmethod
    def from_config(cls, config):
        return AWS(
               api_id=config[cls.SERVICE]['api_id'],
               api_key= config[cls.SERVICE]['api_key'],
               api_region= config[cls.SERVICE]['api_region']
        )

    def process_local(self, out, image_file, min_confidence=MIN_CONFIDENCE):

        image = open(image_file, 'rb')
        content = image.read()

        response = self.client.detect_labels(
            Image={"Bytes": content},
            MinConfidence=min_confidence
        )

        out.save_api_response(image_file, self.SERVICE, response)

        for label_counter, label in enumerate(response["Labels"]):

            label_num = label_counter
            label_name = label["Name"]
            confidence = float(label["Confidence"]) / 100

            out.save_label(image_file, self.SERVICE, label_name, label_num, confidence)