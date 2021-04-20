import boto3
import json
import yaml
import os

secrets = yaml.safe_load(open("secrets.yaml"))

api_id = secrets["aws"]["api_id"]
api_key = secrets["aws"]["api_key"]
api_region = secrets["aws"]["api_region"]

client = boto3.client(
    "rekognition",
    aws_access_key_id=api_id,
    aws_secret_access_key=api_key,
    region_name=api_region,
)

rekog_images_dir = "/media/antonberg/Origenes/Coding/image-taggers/data/"
local_images = os.listdir(rekog_images_dir)

#### Detect labels #####
holder_labels = []

for imageFile in local_images:
    with open(rekog_images_dir + imageFile, "rb") as image:
        content = image.read()
        response = client.detect_labels(Image={"Bytes": content})

    print("Detected labels for " + imageFile)

    if len(response["Labels"]) == 0:
        print("No labels detected")
        temp_dict = {}
        temp_dict["image_id"] = imageFile
        temp_dict["full_detect_labels_response"] = response
        temp_dict["label_num"] = ""
        temp_dict["label_str"] = ""
        temp_dict["label_conf"] = ""
        holder_labels.append(temp_dict)
        print()

    else:

        label_counter = 1

        for label in response["Labels"]:
            print(label["Name"] + " : " + str(label["Confidence"]))
            temp_dict = {}
            temp_dict["image_id"] = imageFile
            temp_dict["full_detect_labels_response"] = response
            temp_dict["label_num"] = label_counter
            temp_dict["label_str"] = label["Name"]
            temp_dict["label_conf"] = label["Confidence"]
            label_counter += 1  # update for the next label
            holder_labels.append(temp_dict)
            print()

print(len(holder_labels))