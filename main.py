from Cryptodome.SelfTest.IO.test_PKCS8 import clear_key

import interface.options
import stages
import subprocess
import sys
from progress.bar import Bar
import time
from interface import options, data_view
from tqdm import tqdm

from stages import stage_SVG

stages_list = {
    'CollectData': stages.stage_CollectData,
    'GetGPT' : stages.stage_GPT,
    'GenerateSVG' : stages.stage_SVG,
    'SkipSelectionLayer' : stages.stage_skipp_selection_layer,
    'GenerateAudio' : stages.stage_GenerateAudio,
    'FilterAudio': stages.stage_FilterAudio,
    'GenerateSUB' : stages.stage_GenerateSUB,
    'Editing' : stages.stage_Edit
}

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_stage(stage, client, bars=None):
    try:
        ids = stages_list[stage](client)
        if not bars is None:
            update_bars(ids, bars)
    except Exception as e:
        print(f'Exception when running {stage}:{str(e)}')
        print('Ignoring error, proceeding to next stage')

def return_progressbar(id, stage, pos):
    t = tqdm(total=8, desc=str(id), position=pos, ncols=80, miniters=1, mininterval=0)
    for x in range(int(stage)):
        t.update()
    return t

def return_progressbars(content):
    r = dict()
    n = 0
    for x in content:
        r[str(x[0])] = return_progressbar(x[0], x[1], n)
        r[f'stage_{str(x[0])}'] = int(x[1])
        n += 1
    return r

def update_bars(ids:list, bars:dict):
    for id in ids:
        if str(id) in bars:
            bars[str(id)].update()

def display_all_shipping(content, client):
    display_content = [(x[2], stages.get_path(x[2], f'video_{x[2]}.mp4'), x[1]) for x in content]
    n = 0
    while True:
        options.clear_screen()
        cur_display = display_content[n]
        out = data_view.display_shipping(*cur_display)
        if out == '1' and n != 0:
            n -= 1
        elif out == '2' and n != len(display_content)-1:
            n += 1
        elif out == '3':
            stages.update_stage(client, cur_display[0])
            del display_content[n]
            if n > len(display_content)-1:
                n -= 1
            if len(display_content) == 0:
                return None
        elif out == '4':
            return

def run_stages(client,):
    # getting data
    run_stage('CollectData', client)

    content = client.basic_read(None, 'id', 'stage')
    content = [x for x in content if 0<int(x[1])<7]
    content.sort(key=lambda x:int(x[1]))

    options.clear_screen()
    bars = return_progressbars(content)

    # next stage
    run_stage('GetGPT', client, bars)

    # next stage
    run_stage('GenerateSVG', client, bars)

    # selecting content
    content = stages.get_stage_content(client, 3)
    # interface for selecting stories
    for x in range(len(bars)):
        #print('\n')
        pass
    time.sleep(3)
    input('Press any key to continue . . .')

    valid_ids = data_view.display_all(content)

    for x in content:
        if not x[2] in valid_ids:
            client.basic_delete(None, id=int(x[2]))
        else:
            stages.update_stage(client, x[2])

    # next stage
    run_stage('GenerateAudio', client, bars)

    # next stage
    run_stage('FilterAudio', client, bars)

    # next stage
    run_stage('GenerateSUB', client, bars)

    # next stage
    run_stage('Editing', client, bars)

    #shipping
    content = stages.get_stage_content(client, 8)
    display_all_shipping(content, client)

def test_func():
    bar = Bar('Processing', max=20)
    for i in range(20):
        time.sleep(0.2)
        bar.next()
    bar.finish()

def run():
    func_run = {
        "1": {
            "name": "Erste Funktion",
            "func": test_func
        },

    }
    interface.options.zeige_menu(func_run)

def view_content():
    pass

if __name__ == '__main__':
    c = stages.connection()
    stages.clean_content(c)
    run_stages(c)



