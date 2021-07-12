import yaml

from progress.bar import Bar

import azure_vision
import googlecloud
import aws
import common
import output

if __name__ == "__main__":
    args = common.arguments()  ## creates a common parameters sets for all programs

    secrets = yaml.safe_load(open("secrets.yaml"))

    ## azure

    subscription_key = secrets["azure"]["api_key"]
    endpoint = secrets["azure"]["api_url"]

    azure_client = azure_vision.client( subscription_key, endpoint )

    ## google vision

    api_account_info = secrets["google"]["service_account_info"]

    google_client = googlecloud.client( api_account_info )

    ## aws

    api_id = secrets["aws"]["api_id"]
    api_key = secrets["aws"]["api_key"]
    api_region = secrets["aws"]["api_region"]

    aws_client = aws.client( api_id, api_key, api_region )


    out = output.Output()

    if args.folder:
        directory = args.folder
        images = common.image_files( directory )

        bar = Bar('Images labelled', max = len(images) * 3 )

        for image in images:

            ## check if we have the image: if yes, do not re-analyse it
            azure_has = out.has_image( image, "azure_vision" )
            google_has = out.has_image( image, "google_vision")
            aws_has = out.has_image( image, "aws" )

            if azure_has and google_has and aws_has:
                continue ## next image

            azure_vision.process_local( azure_client , out, image)
            bar.next()
            googlecloud.process_local( google_client , out, image)
            bar.next()
            aws.process_local( aws_client, out, image )
            bar.next()

        bar.finish()

        out.export_sql("run.db")
        out.export_pickle("run.pickle")
