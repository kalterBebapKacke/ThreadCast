from Cython.Build.Dependencies import join_path
from noideacore import sql
import shutil
from ai import whisper_test as wh

filter_list = ['͡', '—', '“', '”', '…', '\n']

def filter(text:str):
    for x in filter_list:
        while text.__contains__(x):
            text = text.replace(x, '')
    return text

client = sql.sqlite3('./database', ['audio_samples'])

audio_list = client.basic_read(None, 'id', 'text')

path = join_path('.', 'media', 'audio_samples')
path_new = join_path('.', 'database_voice')

''.replace('\n', '')

audio_length = 0

with open(join_path(path_new, 'metadata.txt'), 'w') as file:
    for audio in audio_list:
        audio_name = f'audio_{audio[0]}'
        audio_length += wh.get_audio_length(join_path(path, audio_name + '.mp3'))
        text = filter(audio[1])
        file.write(f'{audio_name}|{text}\n')
        audio_name += '.mp3'
        shutil.copyfile(join_path(path, audio_name), join_path(path_new, 'audio', audio_name))

print(f'Length in min: {audio_length/60}')
print(f'Length in hr: {audio_length/(60*60)}')