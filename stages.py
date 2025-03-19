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
from video import audio, editing
import shutil
from random import randrange
import logging
from ai import filter_abreviations

logging.getLogger("selenium").setLevel(logging.CRITICAL)


tags = '#redditsories #reddit #redditsstories'
logger_name = 'logger'


# Verbesserunsgmöglichkeiten:
# - Ermöglichen weiblicher Stimme
# - zweiten PC nutzen
# - clear moviepy output
# - exception handeling
# - better setup
# - more/better ai
# - voice ai
# - later: config for more customisation
# - fixing main screen
# - SVG verallgemeinern
# - clear chat-gpt output
# - look why undertitle is slightly off


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
    handler = logging.FileHandler(".log", encoding="utf-8", mode='w')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logger.propagate = False
    return logger

def return_logger():
    return logging.getLogger(logger_name)

def save_audio_sample(client, item):
    client.basic_write(['audio_samples'], text=item[0])
    client.basic_write(['audio_samples'], text=item[1])

    id_text = client.basic_read(['audio_samples'], 'id', text=item[0])[0][0]
    id_title = client.basic_read(['audio_samples'], 'id', text=item[1])[0][0]

    scr_path_title = get_path(item[2], 'title.mp3')
    scr_path_text = get_path(item[2], 'text.mp3')
    dest_path = get_path(0, 'media', 'audio_samples', con=False)

    shutil.copy(scr_path_title, dest_path)
    shutil.copy(scr_path_text, dest_path)

    new_path_title = get_path(0, 'media', 'audio_samples', f'audio_{id_title}.mp3', con=False)
    new_path_text = get_path(0, 'media', 'audio_samples', f'audio_{id_text}.mp3', con=False)

    os.rename(join_path(dest_path, 'title.mp3'), new_path_title)
    os.rename(join_path(dest_path, 'text.mp3'), new_path_text)

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
            logger.error(f'Expection when writing new content: {e}')
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
            logger.error(f'Exception occurred when running stage_GPT: {e}')
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
            logger.error(f'Exception occurred when running stage_ReplacingTexts(path={item[2]}): {e}')
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
            logger.error(f'Exception occurred when running stage_SVG(id={item[2]}): {e}')

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
            logger.error(f'Exception occurred when running stage_GenerateAudio(id={item[2]}): {e}')

    num_fails = 0
    for item in content:
        try:
            save_audio_sample(client, item)
        except Exception as e:
            num_fails += 1
            logger.error(f'Exception occurred when saving audio samples(id={item[2]}): {e}')
    logger.debug(f'Saved Audio Samples with no Errors:{len(content)-num_fails}/{len(content)}')


    for item in content:
        if not item[2] in invalid_ids:
            update_stage(client, item[2])
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
            logger.error(f'Exception occurred when running stage_FilterAudio(id={x[2]}): {e}')

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
    # time addition to title
    times = [whisper_test.get_audio_length(get_path(x[2], 'title.mp3')) for x in content]

    # generate srt
    transcripts = list()
    model = whisper_test.model()
    for i, audio_path in enumerate(paths):
        try:
            transcripts.append(whisper_test.generate_single(audio_path, model))
        except Exception as e:
            invalid_ids.append(ids[i])
            transcripts.append(None)
            logger.error(f'Exception occurred when running stage_GenerateSUB(path={audio_path}): {e}')
    del model

    for x in transcripts:
        print(x)

    # convert transcripts to only have that many words
    for x in range(len(transcripts)):
        if not transcripts[x] is None:
            transcripts[x] = whisper_test.json_to_srt(transcripts[x], times[x], chars_per_segment=15)

    #print(transcripts)
    # save transcripts to srt
    for i in range(len(paths)):
        if not transcripts[i] is None:
            with open(get_path(content[i][2], 'transcript.srt'), 'w') as file:
                file.write(str(transcripts[i]))

    # update stages
    _return_ids = list()
    for x in content:
        if not x[2] in invalid_ids:
            #update_stage(client, x[2])
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
        audio_path = random_media(get_path(0, 'media', 'audio', con=False))
        video_path = random_media(get_path(0, 'media', 'video', con=False))
        try:
            editing.create_complex_video2(
                audio_track1_path=get_path(item[2], 'title.mp3'),
                audio_track2_path=get_path(item[2], 'text.mp3'),
                music_path=audio_path,
                video_path=video_path,
                intro_image_path=get_path(item[2], 'Thumnail.png'),
                srt_path=get_path(item[2], 'transcript.srt'),
                output_path=get_path(item[2], f'video_{str(item[2])}.mp4'),
                font_path=font_path,
                tmp_path=get_path(item[2], 'video')
            )
        except Exception as e:
            logger.error(f'Exception occurred when running stage_Edit(path={item[2]}): {e}')
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
    c = connection()
    #clean_content(c)
    logger = create_new_logger()
    #logger.debug('Test')

    #stage_CollectData(c,)
    #stage_GPT(c)
    #stage_SVG(c)

    #stage_replacing_texts(c)

    #stage_GenerateAudio(c)
    #stage_FilterAudio(c)
    stage_GenerateSUB(c)
    #stage_Edit(c)

    #editing.convert_to_vertical(video, target)

    #clean_content(c)
