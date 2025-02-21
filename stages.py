from Cython.Build.Dependencies import join_path
from noideacore import sql
from sympy.parsing.sympy_parser import auto_symbol

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

tags = '#redditsories #reddit #redditsstories'


# Verbesserunsgmöglichkeiten:
# - Ermöglichen weiblicher Stimme
# - zweiten PC nutzen
# - clear moviepy output
# - exception handeling
# - save progress on github
# - better setup
# - render additional videos
# - more/better ai
# - later: config for more customisation
# - progress saving in stage
# - fixing main screen
# - debugging mode
# -


stages = [
    'CollectData', #1
    'GetGPT', #2
    'GenerateSVG', #3
    'Selection', # 4
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
        ids = [x[0] for x in content]
        path = get_path(0, 'content', con=False)
        dirs = os.listdir(path)
        for id in ids:
            if id in dirs:
                shutil.rmtree(get_path(id))
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
    print(_list)
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

def stage_CollectData(client):
    #html = collect.urls.scrape(collect.urls.url6)
    #html = collect.clean.clean_html(html)

    # get better data collection
    '''
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    result=[collect.extract.extract_story(str(x)) for x in articles]
    '''
    result = scrape_v3(data=10)
    for x in result:
        print(x)

    for x in result:
        title = x['title']
        title = title.replace("'", '')
        text = x['content']
        text = ' '.join(text)
        text = text.replace("'", '')
        print(text)
        new_work(client, text, title)
    return None

def stage_GPT(client):
    content = get_stage_content(client, 1)
    print(content)

    texts = [x[0] for x in content]
    titles = [x[1] for x in content]
    ids = [x[2] for x in content]

    #test purpose
    #texts = [texts[0]]
    #titles = [titles[0]]

    _return_text = list()
    _return_title = list()

    # Improvement: Use MP

    for i in range(len(texts)):
        text, title = test_gpt.message(texts[i], titles[i])
        _return_text.append(text)
        _return_title.append(title)

    texts = _return_text
    titles = _return_title

    texts = clean_text(texts)
    titles = clean_text(titles)

    for i, id in enumerate(ids):
        update_stage(client, id, texts[i], titles[i])
    return ids


def stage_SVG(client):
    content = get_stage_content(client, 2)

    #str(PurePath('content', str(id[0])))

    for item in content:
        card.create_reddit(item[1], get_path(item[2], 'Thumnail.svg'))
        card.convert_svg_to_png(get_path(item[2], 'Thumnail.svg'), get_path(item[2], 'Thumnail.png'))

    for item in content:
        update_stage(client, item[2])
    return [x[2] for x in content]

def stage_skipp_selection_layer(client):
    content = get_stage_content(client, 3)
    for item in content:
        update_stage(client, item[2])
    return [x[2] for x in content]

def stage_GenerateAudio(client):
    content = get_stage_content(client, 4)

    # test purpose
    #content = [['This is a very long text to test something', 'Title', 1]]
    invalid_ids = list()
    for item in content:
        try:
            evenlabs.generate(item[0], get_path(item[2], 'text'))
            evenlabs.generate(item[1], get_path(item[2], 'title'))
        except Exception:
            invalid_ids.append(item[2])

    for item in content:
        if not item[2] in invalid_ids:
            update_stage(client, item[2])
    return [x[2] for x in content if x[2] not in invalid_ids]

def stage_FilterAudio(client):
    content = get_stage_content(client, 5)

    for x in content:
        title_path = get_path(x[2], 'title.mp3')
        text_path = get_path(x[2], 'text.mp3')
        content_path = get_path(x[2])

        audio.filter_audio(text_path, title_path, content_path)

    for x in content:
        update_stage(client, x[2])
    return [x[2] for x in content]

def stage_GenerateSUB(client):
    content = get_stage_content(client, 6)
    ids = [x[2] for x in content]
    invalid_ids = list()
    #test purpose
    #content = [['lol', 'lol2', 1]]
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
        except Exception:
            invalid_ids.append(ids[i])
            transcripts.append(None)
    del model

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
            update_stage(client, x[2])
            _return_ids.append(x[2])
    return _return_ids

def stage_Edit(client):
    content = get_stage_content(client, 7)

    font_path = get_path(0, 'media', 'arial', 'ARIALBD 1.TTF', con=False)

    # more audio + video

    # add mp to make faster

    for item in content:
        audio_path = random_media(get_path(0, 'media', 'audio', con=False))
        video_path = random_media(get_path(0, 'media', 'video', con=False))

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

    for x in content:
        update_stage(client, x[2])
        pass
    return [x[2] for x in content]




if __name__ == '__main__':
    c = connection()
    clean_content(c)
    #stage_CollectData(c)
    #stage_GPT(c)
    #stage_SVG(c)

    #stage_GenerateAudio(c)
    #stage_FilterAudio(c)
    #stage_GenerateSUB(c)
    stage_Edit(c)

    video = get_path(25, 'video.mp4')
    target = get_path(25, 'video_test.mp4')

    #editing.convert_to_vertical(video, target)

    #clean_content(c)
