import os
import yaml
import datetime

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException
from msrest.authentication import CognitiveServicesCredentials

import output
import common

def client( subscription_key, endpoint ):
    client = ComputerVisionClient(
        endpoint, CognitiveServicesCredentials(subscription_key)
    )
    return client

def process_local(client, out, image_file, min_confidence = float( common.config["DEFAULT"]["minimal_confidence"] ) ):

    SERVICE = "azure_vision"

    image = open(image_file, 'rb')

    response = None

    ## check that we are not limited by price tier slow down errors
    while not response:
        try:
            response = client.tag_image_in_stream(image, raw = True)
        except ComputerVisionErrorResponseException as ex:
            if ex.error.error.code == '429': ## error code for too many request for the tier. API returns error codeas as string.
                import time
                time.sleep( 60 )
            else:
                print( ex )
                return ## some other error occured, do not try to classify this image

    out.save_api_response(image_file, SERVICE, response.response.json() )

    for label_counter, tag in enumerate(response.output.tags):
        if tag.confidence > min_confidence:

            label_num = label_counter
            label_name = tag.name
            confidence = tag.confidence

            out.save_label(image_file, SERVICE, label_name, label_num, confidence )

if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    from progress.bar import Bar

    secrets = yaml.safe_load(open("secrets.yaml"))
    subscription_key = secrets["azure"]["api_key"]
    endpoint = secrets["azure"]["api_url"]

    client = ComputerVisionClient(
        endpoint, CognitiveServicesCredentials(subscription_key)
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

        out.export_sql("azure_vision.db")
        out.export_pickle("azure_vision.pickle")
