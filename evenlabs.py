import os
import uuid
import json
import requests
from dotenv import load_dotenv
import elevenlabs as el
load_dotenv()

def elenvenlabs_test(text:str):
    client = el.client.ElevenLabs(api_key=os.environ['key2'])

    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",
        #model_id="eleven_turbo_v2",
        text=text,
    )
    return response

def save_file(response, path):
    save_file_path = f"{path}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    #print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file

def generate(text:str, path):
    audio = elenvenlabs_test(text)
    save_file(audio, path)






