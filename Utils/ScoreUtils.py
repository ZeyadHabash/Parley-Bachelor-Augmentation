import os
from Parley.Utils.ExtractionUtils import *

musescore_command_line = "/Applications/MuseScore\ 3.app/Contents/MacOS/mscore"
class ScoreUtils:

    def save_pdf(pdf_filepath, musicxml_filepath):
        os.system(f"{musescore_command_line} {musicxml_filepath} -o {pdf_filepath} &> /dev/null")

    def wipe_score_colours(composition):
        for note in ExtractionUtils.get_all_notes(composition):
            note.score_colour = None

