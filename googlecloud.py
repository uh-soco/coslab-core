import os
import yaml
import google.oauth2.service_account
from google.cloud import vision
import sqlite3
import datetime
import common

import database


def process_local(client, images, min_confidence = float( common.config["DEFAULT"]["minimal_confidence"] ) ):

    SERVICE = "google_vision"

    out = database.Database("results2.db")

    for imageFile in images:
        image = open(imageFile, "rb")
        content = image.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)

        out.save_api_response(
            imageFile, SERVICE, vision.AnnotateImageResponse.to_json(response)
        )

        for label_counter, label in enumerate(response.label_annotations):
            if label.score > min_confidence:

                label_num = label_counter
                label_name = label.description
                confidence = label.score

                out.save_label(imageFile, SERVICE, label_name, label_num, confidence)


if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    secrets = yaml.safe_load(open("secrets.yaml"))
    api_account_info = secrets["google"]["service_account_info"]

    credentials = google.oauth2.service_account.Credentials.from_service_account_info(
        api_account_info
    )

    client = vision.ImageAnnotatorClient(credentials=credentials)

    if args.folder:
        directory = args.folder
        images = [os.path.join(directory, file) for file in os.listdir(directory)]
        process_local(client, images)
