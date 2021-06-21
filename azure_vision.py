import os
import yaml
import sqlite3
import datetime
import time
import common
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import database


def process_local(client, images, min_confidence = float( common.config["DEFAULT"]["minimal_confidence"] ) ):

    SERVICE = "azure_vision"

    out = database.Database("results2.db")

    for counter, imageFile in enumerate(images):
        image = open(imageFile, "rb")

        ## todo: should we maybe use raw response to ensure we get everything that API returned?
        response = client.tag_image_in_stream(image)
        out.save_api_response(imageFile, SERVICE, response.as_dict())

        ## TODO: Anton, why do we need to sleep here?
        if (counter % 10) == 0:
            time.sleep(60)

        for label_counter, tag in enumerate(response.tags):
            if tag.confidence > min_confidence:

                label_num = label_counter
                label_name = tag.name
                confidence = tag.confidence

                out.save_label(imageFile, SERVICE, label_name, label_num, confidence)


#####################################################################################################33
if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    secrets = yaml.safe_load(open("secrets.yaml"))
    subscription_key = secrets["azure"]["api_key"]
    endpoint = secrets["azure"]["api_url"]

    client = ComputerVisionClient(
        endpoint, CognitiveServicesCredentials(subscription_key)
    )

    if args.folder:
        directory = args.folder
        images = [os.path.join(directory, file) for file in os.listdir(directory)]
        process_local(client, images)
