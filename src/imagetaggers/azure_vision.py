import os
import datetime

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException
from msrest.authentication import CognitiveServicesCredentials

from taggerresults import TaggerResults
import common

class Azure:

    def __init__(self, subscription_key="", endpoint=""):
        self.SERVICE = "azure_vision"

        self.client = ComputerVisionClient(
            endpoint, CognitiveServicesCredentials(subscription_key)
        )

    def process_local(self, out, image_file, min_confidence=common.MIN_CONFIDENCE):

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