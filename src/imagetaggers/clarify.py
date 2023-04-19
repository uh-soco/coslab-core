import json
import os
import datetime

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

from taggerresults import TaggerResults
import common


def _client(api_key):

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    return stub, api_key


def client(config):

    SERVICE = "clarifai"

    return _client(api_key=config[SERVICE]['api_key'])


def process_local(stub, api_key, out, image_file, min_confidence=common.MIN_CONFIDENCE):

    SERVICE = "clarifai"

    with open(image_file, 'rb') as image:
        content = image.read()

    metadata = (('authorization', f'Key {api_key}'),)

    response = stub.PostModelOutputs(
        service_pb2_grpc.PostModelOutputsRequest(
            model_id="aaa03c23b3724a16a56b629203edc62c", #put the model you want
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=content
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )

    if response.status.code != status_code_pb2.SUCCESS:
        print(f"Error: {response.status.description}")
        return

    out.save_api_response(image_file, SERVICE, response)

    for label_counter, concept in enumerate(response.outputs[0].data.concepts):

        label_num = label_counter
        label_name = concept.name
        confidence = float(concept.value)

        if confidence >= min_confidence:
            out.save_label(image_file, SERVICE, label_name, label_num, confidence)


if __name__ == "__main__":
    from progress.bar import Bar

    args = common.arguments()
    config = common.load_config(args.config)
    stub, api_key = client(config)

    out = TaggerResults()

    if args.folder:
        directory = args.folder
        images = common.image_files(directory)

        bar = Bar('Images labelled', max=len(images))

        for image in images:
            process_local(stub, api_key, out, image)
            bar.next()

        bar.finish()

        out.export_sql("clarifai.db")
        out.export_pickle("clarifai.pickle")