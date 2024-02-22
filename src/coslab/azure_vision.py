import os
import datetime

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException
from msrest.authentication import CognitiveServicesCredentials

from .taggerresults import TaggerResults
from .common import *

class Azure:

    SERVICE = "azure"

    def __init__(self, subscription_key="", endpoint=""):
        self.client = ComputerVisionClient(
            endpoint, CognitiveServicesCredentials(subscription_key)
        )

    @classmethod
    def from_config(cls, config):
        return Azure(
               subscription_key=config[cls.SERVICE]['subscription_key'],
               endpoint= config[cls.SERVICE]['endpoint']
        )

    def process_local(self, out, image_file, min_confidence=MIN_CONFIDENCE):

        image = open(image_file, 'rb')

        response = None

        ## check that we are not limited by price tier slow down errors
        while not response:
            try:
                response = self.client.tag_image_in_stream(image, raw=True)
            except ComputerVisionErrorResponseException as ex:
                # error code for too many request for the tier. API returns error codeas as string.
                if ex.error.error.code == '429':
                    import time
                    time.sleep(60)
                else:
                    print(ex)
                    return  # some other error occured, do not try to classify this image

        out.save_api_response(image_file, self.SERVICE, response.response.json())

        for label_counter, tag in enumerate(response.output.tags):
            if tag.confidence > min_confidence:

                label_num = label_counter
                label_name = tag.name
                confidence = tag.confidence

                out.save_label(image_file, self.SERVICE, label_name,
                            label_num, confidence)