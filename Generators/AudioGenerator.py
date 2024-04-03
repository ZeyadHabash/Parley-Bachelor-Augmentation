import os
import random


class AudioGenerator:

    def __init__(self, soundfont_filepath):
        self.soundfont_filepath = soundfont_filepath

    def save_wav(self, wav_filepath, midi_filepath):
        os.system(f"fluidsynth {self.soundfont_filepath} --quiet --no-shell {midi_filepath} -T wav -F {wav_filepath}")

    def save_mp3(self, mp3_filepath, midi_filepath):
        r = random.randint(0, 100000)
        os.system(f"fluidsynth {self.soundfont_filepath} --quiet --no-shell {midi_filepath} -T wav -F ./temp_{r}.wav")
        os.system(f"ffmpeg -y -i ./temp_{r}.wav -vn -ar 44100 -ac 2 -b:a 192k -hide_banner {mp3_filepath} &> /dev/null")
        os.system(f"rm ./temp_{r}.wav")
