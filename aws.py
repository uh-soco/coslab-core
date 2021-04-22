import boto3
import json
import yaml
import os
import common
import sqlite3
import datetime

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
        response = client.detect_labels(
            Image={"Bytes": content},
            MinConfidence=common.config.getfloat("DEFAULT", "minimal_confidence"),
        )
        ## todo: save responses directly to database/json output
        holder_responses.append(response)
        print("Detected labels for " + imageFile)

        for label_counter, label in enumerate(response["Labels"]):
            if label["Confidence"] > 0.55:
                service = "aws"
                image_id = imageFile
                label_num = label_counter
                label_name = label["Name"]
                confidence = label["Confidence"]
                date = datetime.datetime.now()

                # Saving to database
                sql = """INSERT INTO results(image,label,label_num,service,confidence,date) VALUES (?,?,?,?,?,?)"""
                db.execute(
                    sql, (image_id, label_name, label_num, service, confidence, date)
                )
                conn.commit()

            # temp_dict = {}
            # temp_dict["image_id"] = imageFile
            # temp_dict["label_num"] = label_counter
            # temp_dict["label"] = label["Name"]
            # temp_dict["confidence"] = label["Confidence"]
            # holder_labels.append(temp_dict)


if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    secrets = yaml.safe_load(open(args.secrets))

    api_id = secrets["aws"]["api_id"]
    api_key = secrets["aws"]["api_key"]
    api_region = secrets["aws"]["api_region"]

    client = boto3.client(
        "rekognition",
        aws_access_key_id=api_id,
        aws_secret_access_key=api_key,
        region_name=api_region,
    )

    if args.folder:
        directory = args.folder
        images = [os.path.join(directory, file) for file in os.listdir(directory)]
        process_local(client, images)
