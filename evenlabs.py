import os
import uuid
import json
import requests
from dotenv import load_dotenv
import elevenlabs as el
load_dotenv()

def elenvenlabs_test(text:str):
    client = el.client.ElevenLabs(api_key=os.environ['key'])

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


def request_test():
    ans = requests.post(
        'https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB/with-timestamps',
        headers={"xi-api-key": "sk_a39cece8e7a1d169fcd9de3d410640f15852405da1edf1c1", "Content-Type": "application/json"},
        json={'text': 'test', 'model_id': 'eleven_turbo_v2'}
    )
    print(ans.status_code)
    print(ans.content)
    print(ans.json())
    with open('test.json', 'w') as f:
        json.dump(ans.json(), f)
    return ans.content




