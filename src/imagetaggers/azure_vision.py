import os
import datetime

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException
from msrest.authentication import CognitiveServicesCredentials

from taggerresults import TaggerResults
import common


def _client(subscription_key="", endpoint=""):
    client = ComputerVisionClient(
        endpoint, CognitiveServicesCredentials(subscription_key)
    )
    return client


def client(config):

    SERVICE = "azure"

    return _client(subscription_key=config[SERVICE]['api_key'],
                   endpoint=config[SERVICE]['api_url'])


def process_local(client, out, image_file, min_confidence=common.MIN_CONFIDENCE):

    SERVICE = "azure_vision"

    image = open(image_file, 'rb')

    response = None

    ## check that we are not limited by price tier slow down errors
    while not response:
        try:
            response = client.tag_image_in_stream(image, raw=True)
        except ComputerVisionErrorResponseException as ex:
            # error code for too many request for the tier. API returns error codeas as string.
            if ex.error.error.code == '429':
                import time
                time.sleep(60)
            else:
                print(ex)
                return  # some other error occured, do not try to classify this image

    out.save_api_response(image_file, SERVICE, response.response.json())

    for label_counter, tag in enumerate(response.output.tags):
        if tag.confidence > min_confidence:

            label_num = label_counter
            label_name = tag.name
            confidence = tag.confidence

            out.save_label(image_file, SERVICE, label_name,
                           label_num, confidence)


if __name__ == "__main__":
    from progress.bar import Bar

    ## creates a common parameters sets for all programs
    args = common.arguments()
    config = common.load_config(args.config)
    client = client(config)

    out = TaggerResults()

    if args.folder:
        directory = args.folder
        images = common.image_files(directory)

        bar = Bar('Images labelled', max=len(images))

        for image in images:
            process_local(client, out, image)
            bar.next()

        bar.finish()

        out.export_sql("azure_vision.db")
        out.export_pickle("azure_vision.pickle")
