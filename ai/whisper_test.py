import whisper
from mutagen import File
import sys
import stable_whisper
import re
from datetime import datetime, timedelta
from . import srt_edit
import subprocess
from utils import util

def model():
    model = whisper.load_model("medium")
    return model

class model_new:

    def __init__(self):
        self.model = stable_whisper.load_model('base.en', device='cpu')

    def generate(self, path_audio:str, srt_path:str, time:float, output_ass:str):
        result = self.model.transcribe(audio=path_audio, verbose=None)
        result.to_srt_vtt(srt_path, segment_level=False, word_level=True)
        with open(srt_path, 'r') as f:
            #print(f.read())
            pass
        srt_editor = srt_edit.sub_edit(srt_path, output_ass, time)
        srt_editor()


def generate(audio:list):
    _result = list()
    for i in range(len(audio)):
        _model = model()
        result = _model.transcribe(audio[i])

        _result.append(result)
    return _result

def generate_single(audio_path:str, model:whisper.Whisper):
    return model.transcribe(audio_path)

def convert_srt_to_ass(input_path, output_path):
    util.exec_command(['ffmpeg', '-y', '-i', input_path, output_path])

def convert_time_to_srt(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    milliseconds = int((seconds_remainder % 1) * 1000)
    seconds = int(seconds_remainder)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def split_segment_by_chars(segment, chars_per_segment):
    """
    Split a segment into multiple segments based on character count,
    ensuring words are not broken
    """
    words = segment['text'].strip().split()
    new_segments = []
    current_segment = []
    current_char_count = 0

    for word in words:
        # Count chars in word plus space
        word_length = len(word) + 1  # +1 for the space

        # If adding this word would exceed the limit and we already have words
        if current_char_count + word_length > chars_per_segment and current_segment:
            # Join current segment words and add to new_segments
            segment_text = ' '.join(current_segment).strip()
            new_segments.append(segment_text)
            # Reset for next segment
            current_segment = [word]
            current_char_count = word_length
        else:
            # Add word to current segment
            current_segment.append(word)
            current_char_count += word_length

    # Add remaining words if any
    if current_segment:
        segment_text = ' '.join(current_segment).strip()
        new_segments.append(segment_text)

    # Calculate timing for each subsegment
    total_chars = len(segment['text'].strip())
    time_per_char = (segment['end'] - segment['start']) / total_chars

    # Create final segments with timing
    final_segments = []
    char_count = 0

    for text in new_segments:
        segment_chars = len(text)
        new_start = segment['start'] + (char_count * time_per_char)
        char_count += segment_chars + 1  # +1 for the space we removed
        new_end = segment['start'] + (char_count * time_per_char)

        # Ensure we don't exceed original end time
        new_end = min(new_end, segment['end'])

        final_segments.append({
            'start': new_start,
            'end': new_end,
            'text': text
        })

    return final_segments


def json_to_srt(json_data, time, chars_per_segment=0):
    """
    Convert JSON transcript data to SRT format

    Parameters:
    json_data (dict): Input JSON transcript data
    chars_per_segment (int): Maximum characters per segment. If 0, keeps original segmentation
    """
    srt_content = []
    counter = 1

    for segment in json_data['segments']:
        #print(type(segment['start']))
        if chars_per_segment > 0:
            # Split segment if chars_per_segment is specified
            sub_segments = split_segment_by_chars(segment, chars_per_segment)
        else:
            # Keep original segment
            sub_segments = [segment]

        for sub_segment in sub_segments:
            start_time = convert_time_to_srt(sub_segment['start'] + time)
            end_time = convert_time_to_srt(sub_segment['end'] + time)

            # Format: Index number
            srt_content.append(str(counter))

            # Format: Start time --> End time
            srt_content.append(f"{start_time} --> {end_time}")

            # Format: Text content
            srt_content.append(sub_segment['text'])

            # Add blank line between entries
            srt_content.append("")

            counter += 1

    return "\n".join(srt_content)


def get_audio_length(file_path):
    try:
        audio = File(file_path)

        if audio is None:
            raise Exception("Format not supported")

        length = float(audio.info.length)
        return length

    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {str(e)}")
        return None

if __name__ == '__main__':
    m = model_new()
    m.generate('./audio_59.mp3', 'test_trans.srt', 0)
