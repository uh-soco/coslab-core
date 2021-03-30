# -*- coding: utf-8 -*-
"""
Python script for detecting labels with Rekognition
"""

import csv
import boto3
import pickle
import os

########### Paths
# Path to where your want to save the resulting labels
rekog_results_dir = "/media/antonberg/Origenes/Coding/image-taggers/results/"

# Path to where your images are
rekog_images_dir = "/media/antonberg/Origenes/Coding/image-taggers/data/"

########### Connect to AWS Rekognition API
credentials = []

with open(
    "/media/antonberg/Origenes/Coding/image-taggers/keys/anton_accessKeys.csv",
    newline="",
) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        credentials.append(row)

personal_access_key = credentials[0]["Access key ID"]
secret_access_key = credentials[0]["Secret access key"]

# Initialize the boto client to access the Rekogniton api
client = boto3.client(
    "rekognition",
    "us-east-2",
    aws_access_key_id=personal_access_key,
    aws_secret_access_key=secret_access_key,
)

########### Create a list of images to pass through API
# Make a list of all the images in the rekog_data_dir you created
local_images = os.listdir(rekog_images_dir)

##### Detect labels
##
holder_labels = []

for imageFile in local_images:
    with open(rekog_images_dir + imageFile, "rb") as image:
        response = client.detect_labels(Image={"Bytes": image.read()})

    print("Detected labels for " + imageFile)

    ## If no labels detected, still save the info:
    if len(response["Labels"]) == 0:
        print("No Labels Detected")
        temp_dict = {}
        temp_dict["image_id"] = imageFile
        temp_dict["full_detect_labels_response"] = response
        temp_dict["label_num"] = ""
        temp_dict["label_str"] = ""
        temp_dict["label_conf"] = ""
        holder_labels.append(temp_dict)

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

len(holder_labels)

###########
# Write out the results to a csv
with open(
    rekog_results_dir + "awsrekognition_detect_labels.csv", "w", newline=""
) as csvfile:
    fieldnames = [
        "image_id",
        "full_detect_labels_response",
        "label_num",
        "label_str",
        "label_conf",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for entry in holder_labels:
        writer.writerow(entry)