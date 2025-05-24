import os
from Cython.Build.Dependencies import join_path
from pydub import AudioSegment
import subprocess
import numpy as np
from . import remove_silence as rs

def amplify_audio(input_file, gain_factor=1.5):
    """
    Verstärkt eine Audio-Datei (MP3 oder WAV) mit einem einstellbaren Verstärkungsfaktor.

    Parameter:
    - input_file: Pfad zur Eingabe-Audiodatei
    - output_file: Pfad zur Ausgabe-Audiodatei
    - gain_factor: Verstärkungsfaktor (Standard: 1.5)
    """
    output_file = input_file
    try:
        # Dateiendung ermitteln
        file_extension = os.path.splitext(input_file)[1].lower()

        # Audio laden
        audio = AudioSegment.from_file(input_file, format=file_extension[1:])

        # Audio verstärken
        # Umrechnung von Dezibel: +6 dB entspricht etwa einer Verdoppelung der Lautstärke
        amplified_audio = audio + (gain_factor - 1) * 6

        # Maximale Lautstärke begrenzen, um Verzerrungen zu vermeiden
        amplified_audio = amplified_audio.apply_gain(-1 * max(0, amplified_audio.max_dBFS - 0))

        # Ausgabedatei speichern
        output_extension = os.path.splitext(output_file)[1].lower()
        amplified_audio.export(output_file, format=output_extension[1:])

    except Exception as e:
        print(f"Fehler beim Verstärken der Audiodatei: {e}")

def remove_silence(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-af",
        f"silenceremove=stop_periods=-1:stop_silence=0.2:start_silence=0.2:stop_duration=0.2:stop_threshold=-25dB",
        "-loglevel", "error",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        pass
# ffmpeg -i ./text.mp3 -af silenceremove=stop_periods=-1:stop_silence=0.2:start_silence=0.2:stop_duration=0.2:stop_threshold=-25dB ./test.mp3
# ffmpeg -i text.mp3 -af silenceremove=start_periods=1:stop_periods=-1:stop_duration=0.2:start_threshold=-45dB:stop_threshold=-45dB output.mp3

def speed_up_audio(input_path, output_path, speed_factor):
    """
    Beschleunigt eine Audiodatei um den angegebenen Faktor.

    Parameter:
    input_path (str): Pfad zur Eingabe-Audiodatei
    output_path (str): Pfad für die beschleunigte Ausgabedatei
    speed_factor (float): Beschleunigungsfaktor (z.B. 1.5 für 50% schneller)

    Returns:
    None: Speichert die beschleunigte Audiodatei am angegebenen Ausgabepfad
    """
    # Lade die Audiodatei
    audio = AudioSegment.from_file(input_path)

    # Konvertiere zu NumPy Array
    samples = np.array(audio.get_array_of_samples())

    # Berechne neue Länge
    new_length = int(len(samples) / speed_factor)

    # Resample das Audio
    indices = np.round(np.linspace(0, len(samples) - 1, new_length)).astype(int)
    speed_changed_samples = samples[indices]

    # Erstelle neues AudioSegment
    speed_changed_audio = audio._spawn(speed_changed_samples.tobytes())

    # Setze Frame Rate entsprechend dem Speed Factor
    speed_changed_audio.frame_rate = int(audio.frame_rate * speed_factor)

    # Exportiere die beschleunigte Datei
    speed_changed_audio.export(output_path, format=output_path.split('.')[-1])

def filter_audio(text_path, title_path, content_path):
    tmp1 = join_path(content_path, 'tmp_text1.mp3')
    tmp2 = join_path(content_path, 'tmp_text2.mp3')
    tmp3 = join_path(content_path, 'tmp_title.mp3')

    amplify_audio(text_path, 0.25)
    amplify_audio(title_path, 0.25)

    #remove_silence(text_path, tmp1)
    rs.main(input_file=text_path, output_file=tmp1)

    # speed up audio
<<<<<<< HEAD
    speed_up_audio(tmp1, tmp2, 1.12)
    speed_up_audio(title_path, tmp3, 1.12)
=======
    speed_up_audio(tmp1, tmp2, 1.05)
    speed_up_audio(title_path, tmp3, 1.05)
>>>>>>> afc76aa78a748f8a5ba187558dbdec3afb4be4d8

    # remove tmp and unnessasary files
    os.remove(text_path)
    os.remove(title_path)
    os.remove(tmp1)

    os.rename(tmp2, text_path)
    os.rename(tmp3, title_path)





