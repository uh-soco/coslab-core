import os
import yaml
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials


secrets = yaml.safe_load(open("secrets.yaml"))
subscription_key = secrets["azure"]["api_key"]
endpoint = secrets["azure"]["api_url"]

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


# Path to where your images are
rekog_images_dir = "/media/antonberg/Origenes/Coding/image-taggers/data/"

########### Create a list of images to pass through API
# Make a list of all the images in the rekog_data_dir you created
local_images = os.listdir(rekog_images_dir)

holder_categories = []

for imageFile in local_images:
    with open(rekog_images_dir + imageFile, "rb") as image:
        response = client.tag_image_in_stream(image)

    print("Detected tags for " + imageFile)

    ## If no tags detected, still save the info:
    if len(response.tags) == 0:
        print("No labels detected")
        temp_dict = {}
        temp_dict["image_id"] = imageFile
        temp_dict["full_detect_labels_response"] = response
        temp_dict["label_num"] = ""
        temp_dict["label_str"] = ""
        temp_dict["label_conf"] = ""
        holder_categories.append(temp_dict)

    else:

        labels_counter = 1

        for tag in response.tags:
            print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))
            temp_dict = {}
            temp_dict["image_id"] = imageFile
            temp_dict["full_detect_labels_response"] = response
            temp_dict["label_num"] = labels_counter
            temp_dict["label_str"] = tag.name
            temp_dict["label_conf"] = tag.confidence
            labels_counter += 1  # update for the next label
            holder_categories.append(temp_dict)

print(len(holder_categories))