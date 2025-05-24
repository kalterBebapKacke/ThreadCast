from TTS_.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

print(TTS().list_models())

# generate speech by cloning a voice using default settings
tts.tts_to_file(text="It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent.",
                file_path="output.wav",
                speaker_wav="./sample_voice.wav",
                language="en")

tts.tts_to_file(text="Hello world!", speaker_wav="./sample_voice.wav", language="en", file_path="output.wav")