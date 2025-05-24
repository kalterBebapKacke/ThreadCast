import os
import numpy as np
from moviepy.editor import *
from moviepy.video.compositing.transitions import crossfadeout
from moviepy.video.fx import fadeout, fadein
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.resize import resize
import subprocess
import shutil
from utils.util import exec_command
from numba import short


def create_complex_video2(
        audio_track1_path:str,
        audio_track2_path:str,
        video_path:str,
        intro_image_path:str,
        srt_path:str,
        output_path:str,
        font_path:str,
        tmp_path:str,
        video_generator,
):
    video_tmp_path1 = tmp_path + '_tmp1.mp4'
    video_tmp_path2 = tmp_path + '_tmp2.mp4'


    # Laden der Audiodateien
    audio1 = AudioFileClip(audio_track1_path)
    audio2 = AudioFileClip(audio_track2_path)
    #music = AudioFileClip(music_path)

    # Kombinieren der Audiofiles
    combined_audio = CompositeAudioClip([
        audio1,  # Reduziere Lautstärke
        audio2.set_start(audio1.duration),
        #music.set_start(0)  # Musik als Hintergrund
    ])

    videos = list()

    videos.append(VideoFileClip(video_generator.__next__()))
    while sum([x.duration for x in videos]) < combined_audio.duration:
        videos.append(VideoFileClip(video_generator.__next__()))

    video = concatenate_videoclips(videos)

    if video.size[0] * (16/9) == video.size[1]:
        shorts = True
    else:
        shorts = False

    # Laden des Videos
    #video = VideoFileClip(video_path).set_duration(combined_audio.duration)
    #video = convert_to_vertical(video)
    video = video.set_audio(combined_audio)
    video = video.set_duration(combined_audio.duration)

    # Intro-Bild mit Fade-Effekt
    intro_image_clip = ImageClip(intro_image_path)

    if shorts is False:
        image_size = video.size[0] * 1 / 3 - 100
    else:
        image_size = video.size[0] - 100
    intro_image_clip = resize(intro_image_clip, width=image_size)

    intro_image_clip = intro_image_clip \
        .set_duration(audio1.duration) \
        .crossfadeout(0.3)
        # .fadeout(0.3) \

    # Finale Videokomposition
    final_video = CompositeVideoClip([
        video,
        intro_image_clip.set_position('center'),
    ])

    final_video.write_videofile(
        video_tmp_path1,
        codec='libx264', # libx264 mpeg4
        verbose = False,
        logger=None,
    )

    if shorts is False:
        #subtitles
        add_subtitles(video_tmp_path1, srt_path, video_tmp_path2, font_path)

        # vertical
        ffmpeg_vertical(video_tmp_path2, output_path)

        os.remove(video_tmp_path1)
        os.remove(video_tmp_path2)
    else:
        add_subtitles(video_tmp_path1, srt_path, output_path, font_path, shorts=True)
        os.remove(video_tmp_path1)



def convert_to_vertical(input, output, target_width=1080, target_height=1920):
    """
    Konvertiert ein horizontales Video in ein vertikales Format.

    Args:
        input_path (str): Pfad zum Eingangsvideo
        output_path (str): Pfad zum Ausgabevideo
        target_width (int): Zielbreite des vertikalen Videos (Standard: 1080)
        target_height (int): Zielhöhe des vertikalen Videos (Standard: 1920)
    """
    video = VideoFileClip(input)

    # Originalabmessungen
    orig_width = video.w
    orig_height = video.h

    # Skalierungsfaktor berechnen
    scale = max(target_width / orig_width, target_height / orig_height)

    # Video skalieren
    scaled_video = resize(video, scale)

    # Neue Abmessungen nach der Skalierung
    new_width = int(orig_width * scale)
    new_height = int(orig_height * scale)

    # Zuschneiden auf die Zielgröße
    x_center = new_width // 2
    y_center = new_height // 2

    cropped_video = scaled_video.crop(
        x1=x_center - (target_width // 2),
        y1=y_center - (target_height // 2),
        x2=x_center + (target_width // 2),
        y2=y_center + (target_height // 2)
    )

    cropped_video.write_videofile(
        output,
        codec='mpeg4',
    )


def make_subtitles(sub, font_path, outline_width=5):
    generator = lambda txt: TextClip(
        txt=txt,
        font='Arial-Fett',
        fontsize=75,
        color='white',
        align='center',
        stroke_color='black',
        stroke_width=2
    )


    subs = SubtitlesClip(sub, generator)
    subs2 = 's'

    #subs.preview()
    #subtitles = SubtitlesClip(subs, f_p, generator)
    return subs, subs2



def add_subtitles(video_path, subtitle_path, output_path, font_path, shorts:bool=False):
    """
    Fügt eine SRT-Untertiteldatei in ein Video ein.

    :param font_path:
    :param video_path: Pfad zum Eingabevideo
    :param subtitle_path: Pfad zur SRT-Untertiteldatei
    :param output_path: Pfad zum Ausgabevideo mit Untertiteln
    """
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf",
        f"pad=ceil(iw/2)*2:ceil(ih/2)*2, ass={subtitle_path}", #:force_style='Fontname=Arial Bold,FontSize=20,PrimaryColour=&H00FFFFFF,Alignment=10,Outline=2.5,Bold=1
        "-c:a", "copy",
        "-loglevel", "error",
        output_path
    ]
    exec_command(command)

def ffmpeg_vertical(input_path, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf",
        f"pad=ceil(iw/2)*2:ceil(ih/2)*2, crop=in_h*9/16:in_h",
        "-c:a", "copy",
        "-loglevel", "error",
        output_path
    ]
    exec_command(command)



#ffmpeg -i input.mp4 -vf "crop=in_h*9/16:in_h" -c:a copy output.mp4

# ffmpeg -i Unbenannt.webm -vf "scale=-1:iw" output.webm

if __name__ == '__main__':
    print(TextClip.list("font"))