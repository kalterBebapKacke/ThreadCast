<<<<<<< HEAD
import os
import srt
import datetime
import pysrt
import pysubs2
from Cython.Build.Dependencies import join_path

off_time = datetime.timedelta(seconds=0.025)

class sub_edit:

    def __init__(self, path_to_srt:str, path_to_ass:srt, add_time:float):
        self.main_style = pysubs2.SSAStyle(
            fontname=os.environ['sub_fontname'],
            fontsize=float(os.environ['sub_fontsize']),
            primarycolor=pysubs2.Color(255, 255, 255),
            backcolor=pysubs2.Color(0, 0, 0),
            secondarycolor=pysubs2.Color(0, 0, 0, ),  # Black for border/shadow
            outlinecolor=pysubs2.Color(0, 0, 0),  # Black outline
            outline=float(os.environ['sub_outline']),
            spacing=0.75,
            shadow=0,
            alignment=pysubs2.Alignment(float(os.environ['sub_alignment'])),
            bold=True if os.environ['sub_bold'] == 'true' else False,
        )

        self.highlighter = Highlighter()
        self.effects = Effects()

        self.if_highlight = True if os.environ['sub_highlight'] == 'true' else False
        self.word_max = float(os.environ['sub_word_max'])
        self.if_one_word_only = True if os.environ['sub_one_word_only'] == 'true' else False
        self.if_separate = True if os.environ['sub_separate_on_period'] == 'true' else False




        self.path_to_srt = path_to_srt
        self.add_time = add_time
        self.path_to_ass = path_to_ass

    def __call__(self):
        sub_file = pysubs2.load(self.path_to_srt)
        sub_file.styles["MainStyle"] = self.main_style
        if self.if_highlight:
            sub_file.styles["Highlight"] = self.highlighter.return_highlighted_style(self.main_style)
        subs = sub_file.events

        # create subtitles
        if self.if_one_word_only is True:
            subs = self.one_word_only(subs)
        elif self.if_separate is True:
            subs = self.short_subtitles(subs)
        else:
            subs = self.short_subtitles_no_separation(subs)

        subs = self.shift_subs_time(subs)

        # edit
        subs  = self.effects(subs)

        # build and save
        subs = self.build_finished_subs(subs)
        sub_file.events = subs
        sub_file.save(self.path_to_ass)
        
    def add_subtitle(self, cur_word:str, index:int, start, end, all_subs:list, highlight_words:bool=False, sub_list:list=()):
        if highlight_words is True: #{\c&H0000FF&\b1}highlighted{\r}
            return self.highlighter(cur_word, start, end, all_subs, sub_list)
        else:
            all_subs.append(pysubs2.SSAEvent(start=start, end=end, text=cur_word.strip(), style="MainStyle"))
            return all_subs #{\fad(300,300)} #r'{\fad(100,100)}' +

    def short_subtitles(self, subs:list):
        new_subs = list()
        cur_word = ''
        index = 1
        start_time = 0
        last_end = subs[0].end

        for sub in subs:
            if len(cur_word) + len(sub.text) + 1 < self.word_max:
                cur_word = cur_word + sub.text + ' '
            else:
                end_time = sub.start
                #duration = end_time - start_time
                new_subs = self.add_subtitle(cur_word, index, start_time, sub.end, new_subs)
                cur_word = sub.text + ' '
                index += 1
                start_time = end_time

            if cur_word.__contains__('.') or cur_word.__contains__('?') or cur_word.__contains__('!'):
                #end_time = sub.end+datetime.timedelta(seconds=0.45)
                new_subs = self.add_subtitle(cur_word, index, start_time, sub.end, new_subs)
                cur_word = ''
                index += 1
                start_time = sub.end
            #last_end = sub.end

        if cur_word != '':
            new_subs = self.add_subtitle(cur_word, index, start_time, subs[-1].end, new_subs)

        return new_subs

    def one_word_only(self, subs:list):
        new_subs = list()
        index = 1
        sub_start = datetime.timedelta(seconds=0)

        for i, sub in enumerate(subs):
            if i != len(subs)+1:
                end_time = subs[i+1].end
            else:
                end_time = sub.end
            new_subs = self.add_subtitle(sub.text, index, sub_start, end_time, new_subs)
            sub_start = sub.end
            index += 1
        return new_subs

    def short_subtitles_no_separation(self, subs:list):
        word_highlight = self.if_highlight
        new_subs = list()
        cur_word = ''
        cur_sub_list = []
        index = 1
        start_time = 0
        #last_end = subs[0].end

        for i, sub in enumerate(subs):
            #print(cur_word)
            if len(cur_word) + len(sub.text) + 1 < self.word_max:
                cur_word = cur_word + sub.text + ' '
                cur_sub_list.append(sub)
            else:
                end_time = sub.start
                new_subs = self.add_subtitle(cur_word, index, start_time, end_time, new_subs, highlight_words=word_highlight, sub_list=cur_sub_list)
                cur_word = sub.text + ' '
                start_time = end_time
                cur_sub_list = [sub]

        if cur_word != '':
            new_subs = self.add_subtitle(cur_word, index, start_time, subs[-1].end, new_subs, highlight_words=word_highlight, sub_list=cur_sub_list)

        return new_subs

    def subs_cleanup(self, subs:list): #not working
        #last_end = subs[0].start
        for i, sub in enumerate(subs):
            cur_word = sub.text
            if (cur_word.__contains__('.') or cur_word.__contains__('?') or cur_word.__contains__('!')) and i + 1 != len(subs):
                check_sub = subs[i + 1]
                duration = sub.end.total_seconds() - sub.start.total_seconds()
                duration_check = check_sub.end.total_seconds() - check_sub.start.total_seconds()
                if duration < 0.35:
                    new_duration =  datetime.timedelta(seconds=duration_check) - datetime.timedelta(seconds=0.35)
                    if not new_duration.total_seconds() < 0:
                        subs[i + 1].start = subs[i + 1].end - new_duration
                        sub.end = sub.end + new_duration
        for i, sub in enumerate(subs):
            if i + 1 != len(subs):
                check_sub = subs[i + 1]
                if (check_sub.start.total_seconds() - sub.end.total_seconds()) < 0:
                    new_time = (check_sub.start + sub.end).total_seconds() / 2
                    sub.end = datetime.timedelta(seconds=new_time) - off_time
                    subs[i + 1].start = datetime.timedelta(seconds=new_time)
        return subs

    def shift_subs_time(self, subs:list):
        add_time = self.add_time
        for i, sub in enumerate(subs):
            if type(sub) == list:
                for _sub in sub:
                    _sub.shift(s=add_time)
            else:
                sub.shift(s=add_time)
        return subs

    def build_finished_subs(self, subs):
        new_subs = list()
        for sub in subs:
            if type(sub) == list:
                new_subs.extend(sub)
            else:
                new_subs.append(sub)
        return new_subs


class Highlighter:

    def __init__(self):
        self.highlight_color = os.environ['sub_highlight_color']
        self.highlight_font = float(os.environ['sub_highlight_font'])
        self.highlight_word_min = float(os.environ['sub_highlight_word_min'])
        self.highlight_type = os.environ['sub_highlight_type']  # color, background, are possible values

        self.highlight_style = [r'{\rHighlight}', r'{\r}']

    def __call__(self, cur_word: str, start, end, all_subs:list, sub_list: list = ()):
        return_subs = list()
        highlighted_words = ''
        # cur_start = sub_list[0].start
        for i, sub in enumerate(sub_list):
            if (self.highlight_word_min < len(highlighted_words) + len(sub.text)) or len(sub_list) - 1 == i:
                highlighted_words += f' {sub.text}'
                highlighted_words = highlighted_words.strip()

                if len(return_subs) == 0:
                    new_cur_word = cur_word.replace(f'{highlighted_words} ',
                                                    fr'{self.highlight_style[0]}{highlighted_words}{self.highlight_style[1]} ')
                else:
                    new_cur_word = cur_word.replace(f' {highlighted_words} ',
                                                    fr' {self.highlight_style[0]}{highlighted_words}{self.highlight_style[1]} ')

                if i != len(sub_list) - 1:
                    end_time = sub_list[i + 1].start
                else:
                    end_time = end

                if start is None:
                    start = sub.start

                return_subs.append(pysubs2.SSAEvent(start=start, end=end_time, text=new_cur_word.strip(), style="MainStyle"))
                highlighted_words = ''
                start = None
            else:
                highlighted_words += f' {sub.text}'
                if start is None:
                    start = sub.start

        if self.highlight_type == 'background':
            for sub in return_subs:
                sub.layer = 1
            all_subs.append(pysubs2.SSAEvent(start=return_subs[0].start, end=end, text=cur_word.strip(), style="MainStyle"))
        all_subs.append(return_subs)
        return all_subs

    def return_highlighted_style(self, style:pysubs2.SSAStyle):
        highlight_style = style.copy()
        color = hex_to_pysub2_color(replace_all(self.highlight_color, '&', ''))
        if self.highlight_type == 'color':
            return self.color(highlight_style, color)
        elif self.highlight_type == 'background':
            return self.background(highlight_style, color)
        elif self.highlight_type == 'bigger':
            return self.bigger(highlight_style, color)
        else:
            return style

    def color(self, style:pysubs2.SSAStyle, color):
        style.primarycolor = color
        return style

    def background(self, style:pysubs2.SSAStyle, color):
        style.borderstyle = 3
        style.backcolor = color
        return style

    def bigger(self, style:pysubs2.SSAStyle, color):
        style.primarycolor = color
        if self.highlight_font != 0:
            style.fontsize = self.highlight_font
        return style

    def background_back(self):
        # return [r'{\3c&H000000&\4c&H0000FF&\4a&H40&\bord5\shad0\be1}', r'{\r}']
        return [r'{\c&H000000&\3c&HFFFF00&\bord5}', r'{\r}']  # {\c&H000000&\3c&HFFFF00&\bord8}


    def highlight_background(self, subs):
        return_subs = list()
        background_style = self.background_back()
        for sub in subs:
            copy_subs = [x.copy() for x in sub]
            sub = self.replace_junk_styles(sub)
            for copy_sub in copy_subs:
                copy_sub.layer = 1
                for i, style in enumerate(background_style):
                    copy_sub.text = copy_sub.text.replace(self.highlight_style[i], style)
            return_subs.append(sub)
            return_subs.append(copy_subs)
        return return_subs

    def replace_junk_styles(self, subs:list):
        for sub in subs:
            for x in self.highlight_style:
                sub.text = sub.text.replace(x, '')
        return subs



class Effects:

    def __init__(self):
        self.fade_in_duration = float(os.environ['sub_fade_in_duration'])
        self.fade_out_duration = float(os.environ['sub_fade_out_duration'])

        #self.highlighter = highlighter

    def __call__(self, subs):
        if self.fade_out_duration != 0 and self.fade_in_duration != 0:
            subs = self.fade(subs)
        else:
            subs = subs
        return subs

    def fade(self, subs):
        for i, sub in enumerate(subs):
            if type(sub) == list:
                sub[0].text = fr'{{\fad({self.fade_in_duration},0)}}{sub[0].text}'
                sub[-1].text = fr'{{\fad(0,{self.fade_out_duration})}}{sub[-1].text}'
            else:
                sub.text = fr'{{\fad({self.fade_in_duration},{self.fade_out_duration})}}{sub.text}'
        return subs


def hex_to_pysub2_color(hex_color, alpha=0):
    """
    Convert hex color string to pysub2.Color format.

    Args:
        hex_color: A hex string in format 'RRGGBB' (e.g., 'ff0000' for red)
        alpha: Alpha/transparency value (0-255), default 0 (opaque)

    Returns:
        pysub2.Color object
    """

    # Remove '#' if present
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Create pysub2.Color object
    return pysubs2.Color(r, g, b, alpha)

def replace_all(str_:str, replace_from, replace_with):
    while str_.__contains__(replace_from):
        str_ = str_.replace(replace_from, replace_with)
    return str_



def ass_add_transitions(ass_path:str, srt_path:str):
    subs = pysubs2.load(srt_path)  # or .ass file

    fade_in_duration = float(os.environ['sub_fade_in_duration'])
    fade_out_duration = float(os.environ['sub_fade_out_duration'])
    if_bold = True if os.environ['sub_bold'] == 'true' else False
    print(if_bold)
    # Add a style if needed
    main_style = pysubs2.SSAStyle(
        fontname=os.environ['sub_fontname'],
        fontsize=float(os.environ['sub_fontsize']),
        primarycolor=pysubs2.Color(255, 255, 255),
        backcolor=pysubs2.Color(0, 0, 0),
        secondarycolor=pysubs2.Color(0, 0, 0,), # Black for border/shadow
        outlinecolor=pysubs2.Color(0, 0, 0),  # Black outline
        outline=float(os.environ['sub_outline']),
        spacing=0.75,
        shadow=0,
        alignment=pysubs2.Alignment(float(os.environ['sub_alignment'])),  # Bottom center
        bold=if_bold,
    )
    subs.styles["MainStyle"] = main_style

    # Apply fade effects to each line
    for line in subs:
        duration = line.end - line.start  # Duration in milliseconds

        # Create fade in from transparent to opaque, and fade out from opaque to transparent
        fade_tag = rf'\fad({fade_in_duration},{fade_out_duration})'

        # Add the fade effect to the line
        if not line.text.startswith("{"):
            line.text = "{" + fade_tag + "}" + line.text
        else:
            # If there are already tags, insert the fade tag
            line.text = line.text.replace("{", "{" + fade_tag + " ", 1)

        # Apply style
        line.style = "MainStyle"

    # Save as ASS file
    subs.save(ass_path)

def full_srt_edit(path_to_srt, time_start:datetime.timedelta, word_max=14):
    #subs = short_subtitles(path_to_srt, word_max)

    #subs = short_subtitles_no_separation(path_to_srt, True, word_max)
    #subs = add_time(subs, time_start)
    #subs = subs_cleanup(subs)
    # repadding of .
    #write_srt(subs, path_to_srt)

    #return subs
    pass

if __name__ == "__main__":
    path = join_path('..', 'content', '930', 'transcript.srt')
    subs = [x for x in pysubs2.load(path)]
    sub_file = pysubs2.load(path)
    highlight_color = '0000000000'
    print(sub_file.events)
    for sub in subs:
        pass
=======
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
>>>>>>> afc76aa78a748f8a5ba187558dbdec3afb4be4d8


#print(srt.Subtitle())