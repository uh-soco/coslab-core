import json
import os
import datetime

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

from .taggerresults import TaggerResults
from .common import *

class Clarify:

    def __init__(self, api_key):

        self.SERVICE = "clarifai"

        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(channel)

    def process_local(self, out, image_file, min_confidence=MIN_CONFIDENCE):

        with open(image_file, 'rb') as image:
            content = image.read()

        metadata = (('authorization', f'Key {api_key}'),)

        response = self.stub.PostModelOutputs(
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

        out.save_api_response(image_file, self.SERVICE, response)

        for label_counter, concept in enumerate(response.outputs[0].data.concepts):

            label_num = label_counter
            label_name = concept.name
            confidence = float(concept.value)

            if confidence >= min_confidence:
                out.save_label(image_file, self.SERVICE, label_name, label_num, confidence)