import csv
import os
import io
from google.cloud import vision


########### Paths
# Path to where your want to save the resulting labels
rekog_results_dir = "/media/antonberg/Origenes/Coding/image-taggers/results/"
# Path to where your images are
rekog_images_dir = "/media/antonberg/Origenes/Coding/image-taggers/data/"

########### Connect to Google Cloud Vision API
# First run in terminal export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
client = vision.ImageAnnotatorClient()
########### Create a list of images to pass through API
# Make a list of all the images in the rekog_data_dir you created
local_images = os.listdir(rekog_images_dir)

##### Detect labels
holder_labels = []

for imageFile in local_images:
    with open(rekog_images_dir + imageFile, "rb") as image:
        content = image.read()
        image = vision.Image(content=content)
        features = [{"type_": vision.Feature.Type.LABEL_DETECTION, "max_results": 11}]
        requests = [{"image": image, "features": features}]

        response = client.batch_annotate_images(requests=requests)
        # response = client.label_detection(image=image)
        # labels = response.label_annotations

    print("Detected labels for " + imageFile)

    if len(response.responses) == 0:
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

        for image_response in response.responses:
            for label in image_response.label_annotations:
                print(label.description + " : " + str(label.score))
                temp_dict = {}
                temp_dict["image_id"] = imageFile
                temp_dict["full_detect_labels_response"] = label
                temp_dict["label_num"] = label_counter
                temp_dict["label_str"] = label.description
                temp_dict["label_conf"] = label.score
                label_counter += 1  # update for the next label
                holder_labels.append(temp_dict)

len(holder_labels)

###########
# Write out the results to a csv
with open(
    rekog_results_dir + "googlecloud_detect_labels.csv", "w", newline=""
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
