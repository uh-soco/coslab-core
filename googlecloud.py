import os
import yaml
import google.oauth2.service_account
from google.cloud import vision

secrets = yaml.safe_load(open("secrets.yaml"))
api_account_info = secrets["google"]["service_account_info"]

credentials = google.oauth2.service_account.Credentials.from_service_account_info(
    api_account_info
)

rekog_images_dir = "/media/antonberg/Origenes/Coding/image-taggers/data/"
local_images = os.listdir(rekog_images_dir)

client = vision.ImageAnnotatorClient(credentials=credentials)

holder_labels = []

## TOdo: check if it is cheaper to analyse one image at a time or request tags for several images at the same time

for imageFile in local_images:
    with open(rekog_images_dir + imageFile, "rb") as image:
        content = image.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations

    print("Detected labels for " + imageFile)

    if len(labels) == 0:
        print("No Labels Detected")
        temp_dict = {}
        temp_dict["image_id"] = imageFile
        temp_dict["full_detect_labels_response"] = labels
        temp_dict["label_num"] = ""
        temp_dict["label_str"] = ""
        temp_dict["label_conf"] = ""
        holder_labels.append(temp_dict)

    else:

        label_counter = 1

        ## todo: check if there is support to define minimun confidence level on the API call
        ## if not, filter here by requiring that confidence > congigured minimun level

        for label in labels:
            print(label.description + " : " + str(label.score))
            temp_dict = {}
            temp_dict["image_id"] = imageFile
            temp_dict["full_detect_labels_response"] = label
            temp_dict["label_num"] = label_counter
            temp_dict["label_str"] = label.description
            temp_dict["label_conf"] = label.score
            label_counter += 1  # update for the next label
            holder_labels.append(temp_dict)

print(len(holder_labels))
