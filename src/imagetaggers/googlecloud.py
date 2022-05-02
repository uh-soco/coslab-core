import os
import datetime

import google.oauth2.service_account
from google.cloud import vision

import common
from taggerresults import TaggerResults

# online discussion says that you can get up-to 50 results if you want, but let's keep this higher in case their API changes over time.
MAX_RESULTS = 100


def _client(service_account_info=""):

    credentials = google.oauth2.service_account.Credentials.from_service_account_info(
        service_account_info
    )

    client = vision.ImageAnnotatorClient(credentials=credentials)

    return client


def client(config):

    SERVICE = "google"

    return _client(service_account_info=config[SERVICE]["service_account_info"])


def process_local(client, out, image_file, min_confidence=common.MIN_CONFIDENCE):

    SERVICE = "google_vision"

    image = open(image_file, 'rb')
    content = image.read()

    image = vision.Image(content=content)
    response = client.label_detection(image=image, max_results=MAX_RESULTS)

    out.save_api_response(
        image_file, SERVICE, vision.AnnotateImageResponse.to_json(response))

    for label_counter, label in enumerate(response.label_annotations):
        if label.score > min_confidence:

            label_num = label_counter
            label_name = label.description
            confidence = label.score

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

        out.export_sql("google_cloud.db")
        out.export_pickle("google_cloud.pickle")
