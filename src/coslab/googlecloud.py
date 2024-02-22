import os
import datetime

import google.oauth2.service_account
from google.cloud import vision

from .taggerresults import TaggerResults
from .common import *

class GoogleCloud:

    # online discussion says that you can get up-to 50 results if you want, but let's keep this higher in case their API changes over time.
    MAX_RESULTS = 100
    SERVICE = "google"

    def __init__(self, service_account_info=""):
        self.credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info
        )

        self.client = vision.ImageAnnotatorClient(credentials=self.credentials)

    @classmethod
    def from_config(cls, config):
        return GoogleCloud(
               service_account_info=config[cls.SERVICE]['service_account_info']
        )

    def process_local(self, out, image_file, min_confidence=MIN_CONFIDENCE):
        image = open(image_file, 'rb')
        content = image.read()

        image = vision.Image(content=content)
        response = self.client.label_detection(image=image, max_results=GoogleCloud.MAX_RESULTS)

        out.save_api_response(
            image_file, self.SERVICE, vision.AnnotateImageResponse.to_json(response))

        for label_counter, label in enumerate(response.label_annotations):
            if label.score > min_confidence:

                label_num = label_counter
                label_name = label.description
                confidence = label.score

                out.save_label(image_file, self.SERVICE, label_name,
                            label_num, confidence)
