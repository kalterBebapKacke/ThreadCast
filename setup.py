import os
import subprocess
from Cython.Build.Dependencies import join_path
import cv2
from stages import get_path
from moviepy.editor import *

def split_extension(path):
    # Finde den letzten Punkt im Pfad
    last_dot_index = path.rfind('.')

    # Finde den letzten Schrägstrich im Pfad
    last_slash_index = max(path.rfind('/'), path.rfind('\\'))

    # Wenn ein Punkt gefunden wurde und er nach dem letzten Schrägstrich kommt
    if last_dot_index > last_slash_index and last_dot_index != -1:
        return path[:last_dot_index], path[last_dot_index:]
    else:
        # Falls keine Endung vorhanden ist, gib den ursprünglichen Pfad und eine leere Endung zurück
        return path, ''

def get_dimensions_from_path(path:str):
    clip = VideoFileClip(path)
    size = clip.size
    return size[1], size[0]

def render_command(input_path, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf",
        f"scale=-1:1920", #f"scale=-1:iw",
        "-an",
        "-loglevel", "error",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        pass
#ffmpeg -i Unbenannt.webm -vf "scale=-1:iw" output.webm

def prerender_videos():
    acceptable_width = [1920, 2560, ] #3840
    path = get_path(0, 'media', 'video', con=False)
    dirs = os.listdir(path)
    videos = [join_path(path, x) for x in dirs if os.path.isfile(join_path(path, x))]
    for video_path in videos:
        height, width = get_dimensions_from_path(video_path)
        print(width)
        print(height)
        if width * 9 / 16 == height and width in acceptable_width:
            print('rendering video')
            path, extension = split_extension(video_path)
            out = f'{path}_render{extension}'
            render_command(video_path, out)
            os.remove(video_path)


if __name__ == '__main__':
    prerender_videos()
