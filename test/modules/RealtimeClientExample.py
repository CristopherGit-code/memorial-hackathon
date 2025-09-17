# Copyright (c) 2024, 2025, Oracle and/or its affiliates.  All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
# SOURCE: https://github.com/oracle/oci-ai-speech-realtime-python-sdk/blob/main/example-client/src/RealtimeClientExample.py

import asyncio
import pyaudio
import oci
from oci.config import from_file
from oci.auth.signers.security_token_signer import SecurityTokenSigner
import argparse
from oci_ai_speech_realtime import RealtimeSpeechClient, RealtimeSpeechClientListener
from oci.ai_speech.models import RealtimeParameters
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create a FIFO queue
queue = asyncio.Queue()

# Set audio parameters
SAMPLE_RATE = 16000  # Can be 8000 as well
FORMAT = pyaudio.paInt16
CHANNELS = 1
BUFFER_DURATION_MS = 96

# Calculate the number of frames per buffer
FRAMES_PER_BUFFER = int(SAMPLE_RATE * BUFFER_DURATION_MS / 1000)


# Duration until which the session is active. To run forever, set this to -1
SESSION_DURATION = 10

final_messages = []

def audio_callback(in_data, frame_count, time_info, status):
    # This function will be called by PyAudio when there's new audio data
    queue.put_nowait(in_data)
    return (None, pyaudio.paContinue)

# Create a PyAudio object
p = pyaudio.PyAudio()

# Open the stream
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER,
    stream_callback=audio_callback,
)

stream.start_stream()
config = from_file()

async def send_audio(client):
    i = 0
    while not client.close_flag:
        data = await queue.get()

        # Send it over the websocket
        await client.send_data(data)
        i += 1

    if stream.is_active():
        stream.close()

def get_realtime_parameters(customizations, compartment_id):
    realtime_speech_parameters: RealtimeParameters = RealtimeParameters()
    realtime_speech_parameters.language_code = "en-US"
    realtime_speech_parameters.model_domain = RealtimeParameters.MODEL_DOMAIN_GENERIC
    realtime_speech_parameters.model_type = "ORACLE"
    realtime_speech_parameters.partial_silence_threshold_in_ms = 0
    realtime_speech_parameters.final_silence_threshold_in_ms = 2000
    realtime_speech_parameters.encoding = (
        f"audio/raw;rate={SAMPLE_RATE}"  # Default=16000 Hz
    )
    realtime_speech_parameters.should_ignore_invalid_customizations = False
    realtime_speech_parameters.stabilize_partial_results = (
        RealtimeParameters.STABILIZE_PARTIAL_RESULTS_NONE
    )
    realtime_speech_parameters.punctuation = RealtimeParameters.PUNCTUATION_NONE

    # Skip this if you don't want to use customizations
    for customization_id in customizations:
        realtime_speech_parameters.customizations = [
            {
                "compartmentId": compartment_id,
                "customizationId": customization_id,
            }
        ]

    return realtime_speech_parameters


class MyListener(RealtimeSpeechClientListener):
    def on_result(self, result):
        if result["transcriptions"][0]["isFinal"]:
            logger.info(
                f"Received final results: {result['transcriptions'][0]['transcription']}"
            )
            final_messages.append(str(result['transcriptions'][0]['transcription']))
        else:
            logger.info(
                f"Received partial results: {result['transcriptions'][0]['transcription']}"
            )

    def on_ack_message(self, ackmessage):
        return super().on_ack_message(ackmessage)

    def on_connect(self):
        return super().on_connect()

    def on_connect_message(self, connectmessage):
        return super().on_connect_message(connectmessage)

    def on_network_event(self, ackmessage):
        return super().on_network_event(ackmessage)

    def on_error(self, error_message):
        return super().on_error(error_message)

    def on_close(self, error_code, error_message):
        print(f"Closed due to error code {error_code}:{error_message}")


async def start_realtime_session(customizations=[], compartment_id=None, region=None):
    def message_callback(message):
        logger.info(f"Received message: {message}")
    
    realtime_speech_parameters = get_realtime_parameters(
        customizations=customizations, compartment_id=compartment_id
    )

    realtime_speech_url = f"wss://realtime.aiservice.{region}.oci.oraclecloud.com"
    client = RealtimeSpeechClient(
        config=config,
        realtime_speech_parameters=realtime_speech_parameters,
        listener=MyListener(),
        service_endpoint=realtime_speech_url,
        # signer=authenticator(),
        compartment_id=compartment_id,
    )

    # example close condition
    async def close_after_a_while(realtime_speech_client, session_duration_seconds):
        if session_duration_seconds >= 0:
            await asyncio.sleep(session_duration_seconds)
            realtime_speech_client.close()

    asyncio.create_task(send_audio(client))

    asyncio.create_task(close_after_a_while(client, SESSION_DURATION))

    await client.connect()

    logger.info("Closed now")

    logger.info("Final messages text:")
    for message in final_messages:
        logger.info(message)

if __name__ == "__main__":
    asyncio.run(
        start_realtime_session(
            customizations=[],
            compartment_id=os.environ.get("COMPARTIMENT"),
            region="us-phoenix-1",
        )
    )