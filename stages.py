import datetime
from Cython.Build.Dependencies import join_path
from noideacore import sql
from sympy.parsing.sympy_parser import auto_symbol
import logging
from ai import test_gpt
from ai import whisper_test
from Thumnials import card
import os
from pathlib import Path, PurePath
import evenlabs
from collect.scrape import scrape_v3
#from setup.base_config import new_config
from video import audio, editing
import shutil
from random import randrange
import logging
from ai import filter_abreviations
import random
import json
import traceback
from utils import base_config
from utils.util import exec_command, return_logger

logging.getLogger("selenium").setLevel(logging.CRITICAL)


tags = '#redditsories #reddit #redditsstories'
logger_name = 'logger'


# Verbesserunsgmöglichkeiten:
# - Ermöglichen weiblicher Stimme
# - zweiten PC nutzen
# - clear moviepy output
# - better setup
# - more/better ai
# - voice ai
# - later: config for more customisation
# - SVG verallgemeinern
# - clear chat-gpt output
# - cache folder
# - editing: image and subtitles
# - better minecraft clips (later)
# - automatic download
# - get rid of slight delay on subtitles
# - cv for downloading clips
#

stages = [
    'CollectData', #1
    'GetGPT', #2, or Replace Text
    'Selection', # 3
    'GenerateSVG' # 4
    'GenerateAudio', # 5
    'FilterAudio',  # 6
    'GenerateSUB', #7
    'Editing', # 8
    'Shipping', # 9
]

def connection():
    client = sql.sqlite3('./database', ['stages'])
    return client

def get_path(id:int, *args, con=True):
    args = [str(x) for x in args]
    if con:
        id = str(id)
        p = PurePath('content', id, *args)
    else:
        p = PurePath(*args)
    return str(p)

def clean_content(client):
    # remove old content
    content = client.basic_read(None, 'id')
    ids = [x[0] for x in content]
    path = get_path(0, 'content', con=False)
    dirs = os.listdir(path)
    for dir in dirs:
        if int(dir) not in ids:
            shutil.rmtree(get_path(int(dir)))
            #os.removedirs(get_path(int(dir)))
    # remove already shipped content
    try:
        content = get_stage_content(client, 9)
        ids = [x[2] for x in content]
        path = get_path(0, 'content', con=False)
        dirs = os.listdir(path)
        for id in ids:
            if str(id) in dirs:
                shutil.rmtree(get_path(id))
    except Exception:
        print('clean content is not working properly')
    try:
        content = client.basic_read(None, 'id')
        ids = [str(x[0]) for x in content]
        path = get_path(0, 'content', con=False)
        dirs = os.listdir(path)
        for id in ids:
            if not id in dirs:
                client.basic_delete(None, id=id)

    except Exception:
        print('clean content is not working properly')

def random_media(dir:str):
    dirs = os.listdir(dir)
    files = [x for x in dirs if os.path.isfile(join_path(dir, x))]
    if len(files) != 1:
        rand_number = randrange(0, len(files)-1)
    else:
        rand_number = 0
    return join_path(dir, files[rand_number])

def random_media_generator(dir:str):
    dirs = os.listdir(dir)
    files = [x for x in dirs if os.path.isfile(join_path(dir, x))]
    random.shuffle(files)
    if len(files) != 0:
        for file in files:
            yield join_path(dir, file)


def new_work(client, text:str, title:str):
    client.basic_write(None, stage=1, text=text, title=title)
    id = client.basic_read(None, 'id', stage=1, text=text, title=title)[0]
    os.mkdir(get_path(id[0]))

def update_stage(client, id:int, text_:str='', title_=''):
    #print(client.basic_read(None, 'stage', 'text', 'title', id=id))
    stage, text, title = client.basic_read(None, 'stage', 'text', 'title', id=id)[0]

    change = {}
    stage = int(stage) + 1

    change['stage'] = stage
    if text_ != '':
        change['text'] = text_
    if title_ != '':
        change['title'] = title_
    client.basic_update(None, change, id=id)

def clean_text(_list:list):
    _return = list()
    #print(_list)
    for x in _list:
        x = x.replace('-', ' ')
        x = x.replace('"', '')
        x = x.replace("\\", '')
        x = x.replace("'", '')
        x = x.replace('\n', ' ')
        x = x.replace('  ', ' ')
        number = x.find(':')
        x = x[number+1:]
        x = x.strip()
        x = remove_parentheses(x)
        _return.append(x)
    return _return

def remove_parentheses(text):
    result = ""
    skip = 0
    for char in text:
        if char == '(':
            skip += 1
        elif char == ')' and skip > 0:
            skip -= 1
        elif skip == 0:
            result += char
    return result

def get_stage_content(client, stage:id):
    _return = client.basic_read(None, 'text', 'title', 'id', stage=stage)
    return _return

def create_new_logger():
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(join_path('cache', '.log'), encoding="utf-8", mode='w')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logger.propagate = False
    return logger

def return_logger():
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        logger = create_new_logger()
    return logger

class config_class:

    def __init__(self):
        self.path = get_path(0, 'cache', 'config.json', con=False)
        if os.path.exists(self.path):
            with open(self.path, 'r') as config_file:
                self.config: dict = json.load(config_file)
        else:
            self.config: dict = self.create_new()

    def create_new(self):
        new_config = base_config.new_config
        tables = [table for table in os.listdir(new_config['args']['video_table_location']) if not os.path.isdir(join_path(new_config['args']['video_table_location'], table))]
        for table in tables:
            new_config['download_content'][str(table).split('.')[0]] = []
        return new_config

    def load_new_values(self):
        new_config = base_config.new_config
        for key in self.config.keys():
            if (type(self.config[key]) == str) or (type(self.config[key]) == tuple):
                new_config[key] = self.config[key]
            else:
                new_config[key] = self._load(self.config[key], new_config[key])
        self.config = new_config

    def _load(self, old, new):
        if type(old) == list and type(new) == list:
            new = [*new, *old]
            return new
        elif type(old) == dict and type(new) == dict:
            for key in old.keys():
                if (type(old[key]) == str) or (type(old[key]) == tuple):
                    new[key] = old[key]
                else:
                    if not key in new.keys():
                        new[key] = old[key]
                    else:
                        new[key] = self._load(old[key], new[key])
            return new

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value

    def save_config(self):
        with open(self.path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def load_args(self):
        args: dict = self.config['args']
        for key in args.keys():
            os.environ[key] = args[key]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_config()

def save_audio_sample(client, item, invalid_ids:list):

    if not item[2] in invalid_ids:
        scr_path_title = get_path(item[2], 'title.mp3')
        scr_path_text = get_path(item[2], 'text.mp3')
        dest_path = get_path(0, 'media', 'audio_samples', con=False)

        if os.path.isfile(scr_path_text):
            client.basic_write(['audio_samples'], text=item[0].replace("'" , ''))
        if os.path.isfile(scr_path_text):
            client.basic_write(['audio_samples'], text=item[1].replace("'" , ''))
        id_text = client.basic_read(['audio_samples'], 'id', text=item[0].replace("'" , ''))[0][0]
        id_title = client.basic_read(['audio_samples'], 'id', text=item[1].replace("'" , ''))[0][0]


        shutil.copy(scr_path_title, dest_path)
        shutil.copy(scr_path_text, dest_path)

        new_path_title = get_path(0, 'media', 'audio_samples', f'audio_{id_title}.mp3', con=False)
        new_path_text = get_path(0, 'media', 'audio_samples', f'audio_{id_text}.mp3', con=False)

        os.rename(join_path(dest_path, 'title.mp3'), new_path_title)
        os.rename(join_path(dest_path, 'text.mp3'), new_path_text)
    else:
        raise RuntimeError

def stage_CollectData(client):
    #html = collect.urls.scrape(collect.urls.url6)
    #html = collect.clean.clean_html(html)

    # get better data collection
    logger = return_logger()
    logger.info('Now running stage_CollectData')

    result = scrape_v3(data=10)

    logger.debug('Collected data')

    content = get_stage_content(client, stage=1)
    texts = [x[1] for x in content]

    for x in result:
        try:
            title = x['title']
            title = title.replace("'", '')
            text = x['content']
            text = ' '.join(text)
            text = text.replace("'", '')
            #print(text)
            if not text in texts:
                new_work(client, text, title)
                pass
        except Exception as e:
            logger.error(f'Expection when writing new content: {e}\n{traceback.format_exc()}')
    logger.info('Finished with stage_CollectData')
    return None

def stage_GPT(client):
    content = get_stage_content(client, 1)
    logger = return_logger()
    logger.info('Now running stage_GPT')
    #print(content)

    texts = [x[0] for x in content]
    titles = [x[1] for x in content]
    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    #test purpose
    #texts = [texts[0]]
    #titles = [titles[0]]

    _return_text = list()
    _return_title = list()

    model = test_gpt.model()
    logger.debug('Created Model for gpt')

    for i in range(len(texts)):
        try:
            text, title = test_gpt.message(texts[i], titles[i], model)
            _return_text.append(text)
            _return_title.append(title)
        except Exception as e:
            _return_text.append('')
            _return_title.append('')
            logger.error(f'Exception occurred when running stage_GPT: {e}\n{traceback.format_exc()}')
    del model

    texts = _return_text
    titles = _return_title

    texts = clean_text(texts)
    titles = clean_text(titles)

    valid_ids = list()

    for i, id in enumerate(ids):
        if not _return_text == '':
            update_stage(client, id, texts[i], titles[i])
            valid_ids.append(id)
    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {[id for id in ids if not id in valid_ids]}')
    logger.info('Finished with stage_GPT')
    return valid_ids

def stage_replacing_texts(client):
    content = get_stage_content(client, 1)
    logger = return_logger()

    logger.debug('Now running stage_ReplacingTexts')

    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    titles = list()
    texts = list()
    invalid_ids = list()

    for item in content:
        try:
            title = filter_abreviations.expand_abbreviations(item[1],
                                                             abbreviation_dict=filter_abreviations.abbreviations)
            text = filter_abreviations.expand_abbreviations(item[0],
                                                            abbreviation_dict=filter_abreviations.abbreviations)

            titles.append(title)
            texts.append(text)
        except Exception as e:
            logger.error(f'Exception occurred when running stage_ReplacingTexts(path={item[2]}): {e}\n{traceback.format_exc()}')
            invalid_ids.append(item[2])
            titles.append('')
            texts.append('')

    valid_ids = [id for id in ids if id not in invalid_ids]
    for i in range(len(titles)):
        if titles[i] != '' and texts[i] != '':
            update_stage(client, ids[i], text_=texts[i], title_=titles[i])
    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {invalid_ids}')
    logger.info('Finished with stage_ReplacingTexts')
    return valid_ids

def stage_skipp_selection_layer(client):
    logger = return_logger()
    content = get_stage_content(client, 2)
    for item in content:
        update_stage(client, item[2])
    logger.debug('Successfully skipped selection layer')
    return [x[2] for x in content]

def stage_SVG(client):
    content = get_stage_content(client, 3)
    logger = return_logger()
    logger.info('Now running stage_SVG')
    #str(PurePath('content', str(id[0])))
    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    invalid_ids = list()

    for item in content:
        try:
            card.create_reddit(item[1], get_path(item[2], 'Thumnail.svg'))
            card.convert_svg_to_png(get_path(item[2], 'Thumnail.svg'), get_path(item[2], 'Thumnail.png'))
        except Exception as e:
            invalid_ids.append(item[2])
            logger.error(f'Exception occurred when running stage_SVG(id={item[2]}): {e}\n{traceback.format_exc()}')

    for item in content:
        update_stage(client, item[2])
    valid_ids = [x[2] for x in content if not x[2] in invalid_ids]
    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {invalid_ids}')
    logger.info('Finished with stage_SVG')
    return valid_ids

def stage_GenerateAudio(client):
    content = get_stage_content(client, 4)
    logger = return_logger()
    logger.info('Now running stage_GenerateAudio')

    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    # test purpose
    #content = [['This is a very long text to test something', 'Title', 1]]
    invalid_ids = list()
    for item in content:
        try:
            evenlabs.generate(item[0], get_path(item[2], 'text'))
            evenlabs.generate(item[1], get_path(item[2], 'title'))
        except Exception as e:
            #print(e)
            invalid_ids.append(item[2])
            logger.error(f'Exception occurred when running stage_GenerateAudio(id={item[2]}): {e}\n{traceback.format_exc()}')

    num_fails = 0
    for item in content:
        try:
            save_audio_sample(client, item, invalid_ids)
        except Exception as e:
            num_fails += 1
            logger.error(f'Exception occurred when saving audio samples(id={item[2]}): {e}\n{traceback.format_exc()}')
    logger.debug(f'Saved Audio Samples with no Errors:{len(content)-num_fails}/{len(content)}')


    for item in content:
        if not item[2] in invalid_ids:
            update_stage(client, item[2])
            #pass
    valid_ids = [x[2] for x in content if x[2] not in invalid_ids]
    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {invalid_ids}')
    logger.info('Finished with stage_GenerateAudio')
    return valid_ids

def stage_FilterAudio(client):
    content = get_stage_content(client, 5)
    invalid_ids = list()
    logger = return_logger()
    logger.info('Now running stage_FilterAudio')

    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    for x in content:
        title_path = get_path(x[2], 'title.mp3')
        text_path = get_path(x[2], 'text.mp3')
        content_path = get_path(x[2])
        try:
            audio.filter_audio(text_path, title_path, content_path)
        except Exception as e:
            invalid_ids.append(x[2])
            logger.error(f'Exception occurred when running stage_FilterAudio(id={x[2]}): {e}\n{traceback.format_exc()}')

    for x in content:
        if not x[2] in invalid_ids:
            update_stage(client, x[2])
    valid_ids = [x[2] for x in content if not x[2] in invalid_ids]

    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {invalid_ids}')
    logger.info('Finished with stage_GenerateAudio')
    return valid_ids


def stage_GenerateSUB(client):
    content = get_stage_content(client, 6)

    logger = return_logger()
    logger.info('Now running stage_GenerateSUB')

    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    invalid_ids = list()

    # paths to audio
    paths = [get_path(x[2], 'text.mp3') for x in content]

    # path to srt
    paths_srt = [get_path(x[2], 'transcript.srt') for x in content]
    paths_ass = [get_path(x[2], 'transcript.ass') for x in content]

    # time addition to title
    times = [whisper_test.get_audio_length(get_path(x[2], 'title.mp3')) for x in content]

    model = whisper_test.model_new()

    for i, audio_path in enumerate(paths):
        try:
            model.generate(audio_path, paths_srt[i], times[i], paths_ass[i])
        except Exception as e:
            invalid_ids.append(ids[i])
            logger.error(f'Exception occurred when running stage_GenerateSUB(path={audio_path}): {e}\n{traceback.format_exc()}')
    del model

    # update stages
    _return_ids = list()
    for x in content:
        if not x[2] in invalid_ids:
            update_stage(client, x[2])
            _return_ids.append(x[2])
    valid_ids = [x[2] for x in content if not x[2] in invalid_ids]

    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {invalid_ids}')
    logger.info('Finished with stage_GenerateSUB')
    return _return_ids

def stage_Edit(client):
    content = get_stage_content(client, 7)

    logger = return_logger()
    logger.info('Now running stage_Edit')
    ids = [x[2] for x in content]
    logger.debug(f'Running this stage on these ids: {ids}')

    font_path = get_path(0, 'media', 'arial', 'ARIALBD 1.TTF', con=False)

    invalid_ids = list()

    for item in content:
        video_path = random_media(get_path(0, 'media', 'video', con=False))
        video_generator = random_media_generator(join_path(os.environ['video_location_path'], os.environ['video_use_name']))
        try:
            editing.create_complex_video2(
                audio_track1_path=get_path(item[2], 'title.mp3'),
                audio_track2_path=get_path(item[2], 'text.mp3'),
                video_path=video_path,
                intro_image_path=get_path(item[2], 'Thumnail.png'),
                srt_path=get_path(item[2], 'transcript.ass'),
                output_path=get_path(item[2], f'video_{str(item[2])}.mp4'),
                font_path=font_path,
                tmp_path=get_path(item[2], 'video'),
                video_generator=video_generator
            )
        except Exception as e:
            logger.error(f'Exception occurred when running stage_Edit(id={item[2]}): {e}\n{traceback.format_exc()}')
            invalid_ids.append(item[2])

    valid_ids = [x[2] for x in content if x[2] not in invalid_ids]
    for id in valid_ids:
        update_stage(client, id)
        pass
    logger.debug(f'Valid Ids at the End of stage: {valid_ids}')
    logger.debug(f'Invalid Ids at the End of stage: {invalid_ids}')
    logger.info('Finished with stage_Edit')
    return valid_ids


if __name__ == '__main__':
    cfg = config_class()
    cfg.load_args()
    c = connection()
    clean_content(c)
    logger = create_new_logger()
    #logger.debug('Test')
    #stage_CollectData(c,)
    #stage_GPT(c)
    #stage_SVG(c)
    #stage_replacing_texts(c)
    #stage_GenerateAudio(c)
    #stage_FilterAudio(c)

    stage_GenerateSUB(c)
    stage_Edit(c)

