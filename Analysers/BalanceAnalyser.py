from Parley.Utils.ChordUtils import *
from Parley.Utils.MathUtils import *
from Parley.Utils.ExtractionUtils import *
import numpy as np


class BalanceAnalyser:

    def __init__(self, analysis_spec):
        self.analysis_spec = analysis_spec

    def analyse_chord_sequence(self, composition):
        chord_name_list = []
        for episode in composition.form.episodes:
            for bar in episode.bars:
                for chord in bar.chords:
                    chord_name = ChordUtils.get_chord_name(chord)
                    chord_name_list.append((chord_name, chord))
        elist = [c[0] for c in chord_name_list]
        window_length = 5
        rolling_entropies = MathUtils.get_rolling_entropies(elist, window_length)
        low_entropy_places = np.where(np.array(rolling_entropies) == min(rolling_entropies))[0]
        bar_nums = []
        previous_lep = -10
        chords_to_colour = []
        for lep in low_entropy_places:
            chord = chord_name_list[lep][1]
            for pos in range(lep, lep + window_length):
                chords_to_colour.append(chord_name_list[pos][1])
            bar_num = chord.parent_bar.comp_bar_num
            if lep - window_length > previous_lep:
                bar_nums.append(bar_num)
                previous_lep = lep
        for note in ExtractionUtils.get_all_notes(composition):
            if note.parent_chord in chords_to_colour:
                note.score_colour = "red"
        return bar_nums
