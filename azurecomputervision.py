from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import csv
import os

"""
Authenticate
Authenticates your credentials and creates a client.
"""
subscription_key = "b4121b5fefeb499480a5d8565460615d"
endpoint = "https://image-rec-validity.cognitiveservices.azure.com/"

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Path to where your want to save the resulting labels
rekog_results_dir = "/media/antonberg/Origenes/Coding/image-taggers/results/"

# Path to where your images are
rekog_images_dir = "/media/antonberg/Origenes/Coding/image-taggers/data/"

########### Create a list of images to pass through API
# Make a list of all the images in the rekog_data_dir you created
local_images = os.listdir(rekog_images_dir)

##### Detect labels

holder_categories = []

for imageFile in local_images:
    with open(rekog_images_dir + imageFile, "rb") as image:
        features = ["categories"]
        results = client.analyze_image_in_stream(image, features)

    print("Detected categories for " + imageFile)

    ## If no categories detected, still save the info:
    if len(results.categories) == 0:
        print("No Categoris Detected")
        temp_dict = {}
        temp_dict["image_id"] = imageFile
        temp_dict["full_detect_labels_response"] = results
        temp_dict["label_num"] = ""
        temp_dict["label_str"] = ""
        temp_dict["label_conf"] = ""
        holder_categories.append(temp_dict)

    else:

        categories_counter = 1

        for category in results.categories:
            print(
                "'{}' with confidence {:.2f}%".format(
                    category.name, category.score * 100
                )
            )
            temp_dict = {}
            temp_dict["image_id"] = imageFile
            temp_dict["full_detect_labels_response"] = results
            temp_dict["label_num"] = categories_counter
            temp_dict["label_str"] = category.name
            temp_dict["label_conf"] = category.score
            categories_counter += 1  # update for the next label
            holder_categories.append(temp_dict)

len(holder_categories)

###########
# Write out the results to a csv
with open(
    rekog_results_dir + "azurecomputervision_detect_labels.csv", "w", newline=""
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
    for entry in holder_categories:
        writer.writerow(entry)