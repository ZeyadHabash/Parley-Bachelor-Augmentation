from Parley.Utils.RhythmUtils import *
from Parley.Utils.SpecUtils import *


class StandardBarStructureGenerator:

    def __init__(self, bar_structure_gen_spec):
        self.bar_structure_gen_spec = bar_structure_gen_spec

    def calculate_empty_bars(self, previous_episode, this_episode):
        bars = []
        spec = self.bar_structure_gen_spec
        comp_bar_num = 0 if previous_episode is None else previous_episode.bars[-1].comp_bar_num + 1
        s = spec.bar_start_target_duration_ms
        f = spec.bar_end_target_duration_ms
        t = spec.episode_target_duration_ms
        n = int((2 * t - s + f) // (2 * s + f - s))
        x = (s - f) / n
        short_t = (n * s) - (x * (n - 1) * n) / 2
        diff = t - short_t
        addon = diff/n
        start_tick = 0 if previous_episode is None else previous_episode.bars[-1].start_tick + previous_episode.bars[-1].duration_ticks
        for i in range(0, n):
            cb_num = comp_bar_num + i
            eb_num = i
            spec = self.bar_structure_gen_spec
            ms_duration = (s - (i * x)) + addon
            bar_duration_ticks = int(round((ms_duration / 1000) * 960))
            bar = Bar(cb_num, eb_num, start_tick, bar_duration_ticks, rhythm=spec.rhythm, chords=[],
                      interestingness_profile=None, score_notes=[])
            start_tick += bar_duration_ticks
            bars.append(bar)

        this_episode.bars = bars

    def add_chord_positions(self, previous_episode, this_episode):
        for bar in this_episode.bars:
            spec = SpecUtils.get_instantiated_copy(self.bar_structure_gen_spec, bar)
            ratio_strings = spec.rhythm.split(",")
            start_duration_details = RhythmUtils.get_start_duration_ticks(bar.duration_ticks, spec.rhythm)
            for ind, [_, _, duration_ticks, _, _] in enumerate(start_duration_details):
                ratio_string = ratio_strings[ind].split(":")[2]
                top = int(ratio_string.split("/")[0])
                bottom = int(ratio_string.split("/")[1])
                chord = Chord(chord_name="cmaj", frac=bottom, num_fracs=top,
                              pitches=[60, 64, 67], duration_ticks=duration_ticks,
                              parent_bar=bar)
                bar.chords.append(chord)