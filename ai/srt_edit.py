import srt
import datetime
import pysrt

def add_subtitle(cur_word:str, index:int, start, end):
    sub = srt.Subtitle(index=index, start=start, end=end, content=cur_word.strip())
    return sub

def short_subtitles(path_to_srt, word_max=15):
    with open(path_to_srt, 'r') as file:
        data = file.read()

    subs = [x for x in srt.parse(data)]
    new_subs = list()
    cur_word = ''
    index = 1
    start_time = datetime.timedelta(0)
    last_end = subs[0].end

    for sub in subs:
        if len(cur_word) + len(sub.content) + 1 < word_max:
            cur_word = cur_word + sub.content + ' '
        else:
            end_time = sub.start
            duration = end_time - start_time
            new_subs.append(add_subtitle(cur_word, index, start_time, end_time))
            cur_word = sub.content + ' '
            index += 1
            start_time = end_time

        if cur_word.__contains__('.') or cur_word.__contains__('?') or cur_word.__contains__('!'):
            end_time = sub.end+datetime.timedelta(seconds=0.45)
            new_subs.append(add_subtitle(cur_word, index, start_time, end_time))
            cur_word = ''
            index += 1
            start_time = end_time
        #last_end = sub.end

    if cur_word != '':
        new_subs.append(add_subtitle(cur_word, index, start_time, subs[-1].end))

    return new_subs

def subs_cleanup(subs:list):
    last_end = subs[0].start
    for sub in subs:
        last_end = sub.end


def add_time(subs:list, time_start:datetime.timedelta):
    for i, sub in enumerate(subs):
        subs[i].start = sub.start + time_start
        subs[i].end = sub.end + time_start
    return subs

def full_srt_edit(path_to_srt, time_start:datetime.timedelta, word_max=14):
    subs = short_subtitles(path_to_srt, word_max)
    subs = add_time(subs, time_start)
    subs_cleanup(subs)

    write_srt(subs, path_to_srt)

    return subs

def format_timedelta(td):
    total_milliseconds = int(td.total_seconds() * 1000)  # truncate instead of round
    hours = total_milliseconds // 3600000
    minutes = (total_milliseconds % 3600000) // 60000
    seconds = (total_milliseconds % 60000) // 1000
    milliseconds = total_milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def write_srt(subtitles, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for sub in sorted(subtitles, key=lambda s: s.index):
            start_str = format_timedelta(sub.start)
            end_str = format_timedelta(sub.end)
            f.write(f"{sub.index}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{sub.content}\n\n")



if __name__ == "__main__":
    time = datetime.timedelta(days=1, hours=4, minutes=5, seconds=33, milliseconds=623, microseconds=22)
    print(time.microseconds)


#print(srt.Subtitle())