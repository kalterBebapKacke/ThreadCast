import os
import subprocess
from Cython.Build.Dependencies import join_path
import cv2

import stages
from stages import get_path, return_logger, config_class
from stages import get_path, create_new_logger, return_logger, config_class
from moviepy.editor import *
import pandas as pd
import traceback

shorts_download_links_cooking = [
    "https://www.youtube.com/shorts/p5RDJPBRcnA",
    "https://www.youtube.com/shorts/wLL8H_h_nvs",
    "https://www.youtube.com/shorts/zPxQjuFoUBc",
    "https://www.youtube.com/shorts/LajkNW1dHE8",
    "https://www.youtube.com/shorts/dOOOeyBAQxQ",
]


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

def download_youtube_video(url, output_path=None, additional_options=None):
    try:

        command = ['yt-dlp', url, '-o', os.path.join(output_path, '%(title)s.%(ext)s')]

        if additional_options:
            pass
            #command.extend(additional_options)

        subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None

def get_dimensions_from_path(path:str):
    clip = VideoFileClip(path)
    size = clip.size
    del clip
    return size[1], size[0]

def render_command(input_path, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-t", str(5 * 60),
        "-i", f"{input_path}",
        "-vf",
        f"scale=-1:1920", #f"scale=-1:iw",
        "-an",
        "-loglevel", "error",
        f"{output_path}"
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        pass
#ffmpeg -i Unbenannt.webm -vf "scale=-1:iw" output.webm

def prerender_videos(path:str, shorts:bool=False, video_names:list=()):
    acceptable_width_videos = [1920, 2560,]
    acceptable_width_shorts = [1080, ]
    dirs = os.listdir(path)
    if video_names == ():
        videos = [join_path(path, x) for x in dirs if os.path.isfile(join_path(path, x))]
    else:
        videos = [join_path(path, x) for x in video_names]
    for video_path in videos:
        height, width = get_dimensions_from_path(video_path)
        if (width * 9 / 16 == height and width in acceptable_width_videos) and not shorts:
            path, extension = split_extension(video_path)
            out = f'{path}_render{extension}'
            render_command(video_path, out)
            if os.path.isfile(out):
                os.remove(video_path)
        if not width in acceptable_width_shorts and shorts:
            path, extension = split_extension(video_path)
            out = f'{path}_render{extension}'
            render_command(video_path, out)
            if os.path.isfile(out):
                os.remove(video_path)

def check_config():
    pass


'''
def video_updater(cfg:config_class):
    path_tables = get_path(0, 'video_tables', con=False)

    tables = [x for x in os.listdir(path_tables) if x.endswith('.csv')]
    names = [split_extension(x)[0] for x in tables]
    json_data = cfg['download_content']

    for name in names:
        if not name in json_data.keys():
            json_data[name] = []
            os.makedirs(get_path(0, 'media', 'video', name, con=False), exist_ok=True)

    for i, table in enumerate(tables):
        name = names[i]
        list_urls:list = json_data[name]
        urls = check_csv_data(get_path(0, 'video_tables', table, con=False), list_urls)

        download_path = join_path(os.environ['video_location_path'], name)

        for url in urls:
            download_youtube_video(url, output_path=download_path)

        prerender_videos(path=download_path, shorts=True) # needs to also work with normal videos
        for url in urls:
            list_urls.append(url)
        #print(list_urls)
        json_data[name] = list_urls

def check_csv_data(path:str, json_info):
    urls = pd.read_csv(path)['url']
    return_urls = list()
    for url in urls:
        if url not in json_info:
            return_urls.append(url)
    return return_urls

def main():
    logger = return_logger()
    with config_class() as cfg:
        cfg.load_new_values()
        cfg.load_args()
        logger.info('loaded args into environment')
        try:
            video_updater(cfg)
            logger.info('Updated video content')
        except Exception as e:
            logger.error(f'Error occurred when updating video content: {e}\n{traceback.format_exc()}')

'''

def video_updater(cfg:config_class):
    path_tables = get_path(0, 'video_tables', con=False)

    tables = [x for x in os.listdir(path_tables) if x.endswith('.csv')]
    names = [split_extension(x)[0] for x in tables]
    json_data = cfg['download_content']

    for name in names:
        if not name in json_data.keys():
            json_data[name] = []
            os.makedirs(get_path(0, 'media', 'video', name, con=False), exist_ok=True)

    for i, table in enumerate(tables):
        name = names[i]
        list_urls:list = json_data[name]
        urls = check_csv_data(get_path(0, 'video_tables', table, con=False), list_urls)

        download_path = join_path(os.environ['video_location_path'], name)

        for url in urls:
            download_youtube_video(url, output_path=download_path)

        prerender_videos(path=download_path, shorts=True)
        for url in urls:
            list_urls.append(url)
        #print(list_urls)
        json_data[name] = list_urls

def check_csv_data(path:str, json_info):
    urls = pd.read_csv(path)['url']
    return_urls = list()
    for url in urls:
        if url not in json_info:
            return_urls.append(url)
    return return_urls

def main():
    logger = return_logger()
    with config_class() as cfg:
        cfg.load_args()
        logger.info('loaded args into environment')
        try:
            video_updater(cfg)
            logger.info('Updated video content')
        except Exception as e:
            logger.error(f'Error occurred when updating video content: {e}\n{traceback.format_exc()}')

if __name__ == '__main__':
    #path = get_path(0, 'media', 'shorts', con=False)
    #prerender_videos(path, shorts=True)
    #video_updater()
    main()
    cfg = stages.config_class()
    #print(cfg.create_new())
    cfg.load_args()
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))


