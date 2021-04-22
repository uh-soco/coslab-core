import os
import yaml
import sqlite3
import datetime
import common
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

conn = sqlite3.connect("results.db")
db = conn.cursor()
db.execute(
    "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, image TEXT, label TEXT, label_num INT, service TEXT, confidence REAL, date DATE )"
)


def process_local(client, images):

    holder_responses = []
    holder_labels = []

    for imageFile in images:
        image = open(imageFile, "rb")
        # content = image.read()
        response = client.tag_image_in_stream(image)
        holder_responses.append(response)
        print("Detected tags for " + imageFile)

        for label_counter, tag in enumerate(response.tags):
            if tag.confidence > 0.55:
                service = "azure"
                image_id = imageFile
                label_num = label_counter
                label_name = tag.name
                confidence = tag.confidence
                date = datetime.datetime.now()

                # Saving to database
                sql = """INSERT INTO results(image,label,label_num,service,confidence,date) VALUES (?,?,?,?,?,?)"""
                db.execute(
                    sql, (image_id, label_name, label_num, service, confidence, date)
                )
                conn.commit()


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