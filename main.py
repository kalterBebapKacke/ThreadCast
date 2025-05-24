import os
from Cython.Build.Dependencies import join_path
from rich.console import Console
import interface.options
import stages
import subprocess
import sys
from progress.bar import Bar
import time
from interface import options, data_view #progessbar_custom
from tqdm import tqdm
from rich.progress import Progress, BarColumn, TextColumn
import traceback

from stages import stage_SVG

stages_list = {
    'CollectData': stages.stage_CollectData,
    'GetGPT' : stages.stage_replacing_texts,
    'GenerateSVG' : stages.stage_SVG,
    'SkipSelectionLayer' : stages.stage_skipp_selection_layer,
    'GenerateAudio' : stages.stage_GenerateAudio,
    'FilterAudio': stages.stage_FilterAudio,
    'GenerateSUB' : stages.stage_GenerateSUB,
    'Editing' : stages.stage_Edit
}

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_stage(stage, client, logger, bars=None, progress:Progress=None, stage_num=0, run_stage_int:int=0, start_from:bool=True):
    try:
        if (run_stage_int <= stage_num and start_from is True) or (run_stage_int == stage_num and start_from is False):
            ids = stages_list[stage](client)
            if not bars is None:
                update_bars(ids, bars, progress)
    except Exception as e:
        logger.error(f'Exception when running {stage}:{str(e)}')
        logger.info('Ignoring error, proceeding to next stage')

def return_progressbars(content, progress:Progress):
    r = dict()
    for x in content:
        bar = progress.add_task(str(x[0]), total=8)
        for i in range(x[1]):
            progress.update(bar, advance=1)
        r[str(x[0])] = bar
    return r

def update_bars(ids:list, bars:dict, progress:Progress):
    for id in ids:
        if str(id) in bars:
            progress.update(bars[str(id)], advance=1)

def visible_bars(bars, progress:Progress, show:bool=False):
    for bar in bars:
        progress.update(bars[bar], visible=show)


def display_all_shipping(content, client):
    display_content = [(x[2], join_path(os.getcwd(), stages.get_path(x[2], f'video_{x[2]}.mp4')), x[1]) for x in content]
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

def select_content(client, content):
    input('Press any key to continue . . .')

    valid_ids, ignore_ids = data_view.display_all(content)

    for x in content:
        if not x[2] in valid_ids:
            if not x[2] in ignore_ids:
                client.basic_delete(None, id=int(x[2]))
                client.basic_write(['selecting_info'], title=x[1], text=x[0], selected='False')
        else:
            stages.update_stage(client, x[2])
            client.basic_write(['selecting_info'], title=x[1], text=x[0], selected='True')
    return valid_ids

def run_stages(client, progress, logger, run_stage_int:int=0, start_from:bool=True):
    stages.clean_content(client)
    # getting data

    run_stage('CollectData', client, logger, stage_num=0, run_stage_int=run_stage_int, start_from=start_from)

    progress.start()

    content = client.basic_read(None, 'id', 'stage')
    content = [x for x in content if 0<int(x[1])<7]
    content.sort(key=lambda x:int(x[1]))

    bars = return_progressbars(content, progress)

    # next stage
    run_stage('GetGPT', client, logger, bars, progress=progress, stage_num=1, run_stage_int=run_stage_int, start_from=start_from)

    # next stage

    if (run_stage_int <= 2 and start_from is True) or (run_stage_int == 2 and start_from is False):
        logger.info('Now selecting content')
        content = stages.get_stage_content(client, 2)

        logger.debug(f'Now selecting from these ids:{[x[2] for x in content]}')

        time.sleep(2)

        progress.stop()
        options.clear_screen()
        if len(content) != 0:
            ids = select_content(client, content)

            logger.debug(f'Selected ids: {ids}')

            input('Press any key to continue . . .')

            options.clear_screen()

            progress.__init__()

            content = client.basic_read(None, 'id', 'stage')
            content = [x for x in content if 0 < int(x[1]) < 7]
            content.sort(key=lambda x: int(x[1]))

            bars = return_progressbars(content, progress)

        #visible_bars(bars, progress, True)
        progress.start()
        time.sleep(2)

    # next stage
    run_stage('GenerateSVG', client, logger, bars, progress=progress, stage_num=3, run_stage_int=run_stage_int, start_from=start_from)

    # next stage
    run_stage('GenerateAudio', client, logger, bars, progress=progress, stage_num=4, run_stage_int=run_stage_int, start_from=start_from)

    # next stage
    run_stage('FilterAudio', client, logger, bars, progress=progress, stage_num=5, run_stage_int=run_stage_int, start_from=start_from)

    # next stage
    run_stage('GenerateSUB', client, logger, bars, progress=progress, stage_num=6, run_stage_int=run_stage_int, start_from=start_from)

    # next stage
    run_stage('Editing', client, logger, bars, progress=progress, stage_num=7, run_stage_int=run_stage_int, start_from=start_from)

    #shipping
    progress.stop()
    options.clear_screen()
    if (run_stage_int <= 8 and start_from is True) or (run_stage_int == 8 and start_from is False):
        options.clear_screen()
        content = stages.get_stage_content(client, 8)
        if len(content) != 0:
            display_all_shipping(content, client)

def wrapper_run(client):
    logger = stages.create_new_logger()
    console = Console(force_terminal=True)
    cfg = stages.config_class()
    cfg.load_args()
    progress: Progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=console
    )
    try:
<<<<<<< HEAD
        run_stages(client, progress, logger, 3, True)
=======
        run_stages(client, progress, logger, 7, True)
>>>>>>> afc76aa78a748f8a5ba187558dbdec3afb4be4d8
    except Exception as e:
        try:
            progress.stop()
        except Exception:
            logger.debug('Failed to close Progressbar render')
        logger.error(f'Error when running stages:{e}\n{traceback.format_exc()}')

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
    wrapper_run(c)



