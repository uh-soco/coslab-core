import os
import yaml
import google.oauth2.service_account
from google.cloud import vision
import sqlite3
import datetime
import common

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
        content = image.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        holder_responses.append(response)
        print("Detected labels for " + imageFile)

        for label_counter, label in enumerate(response.label_annotations):
            if label.score > 0.55:
                service = "googlevision"
                image_id = imageFile
                label_num = label_counter
                label_name = label.description
                confidence = label.score
                date = datetime.datetime.now()

                # Saving to database
                sql = """INSERT INTO results(image,label,label_num,service,confidence,date) VALUES (?,?,?,?,?,?)"""
                db.execute(
                    sql, (image_id, label_name, label_num, service, confidence, date)
                )
                conn.commit()


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