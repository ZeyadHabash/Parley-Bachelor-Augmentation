from Parley.Utils.NROUtils import *
from Parley.Utils.SpecUtils import *


class NRTChordSequenceGenerator:

    def __init__(self, chord_sequence_gen_spec):
        self.chord_sequence_gen_spec = chord_sequence_gen_spec

    def update_chords(self, previous_episode, this_episode, next_episode):

        spec = SpecUtils.get_instantiated_copy(self.chord_sequence_gen_spec, this_episode.bars[0])
        next_pitches = None
        if previous_episode is not None and spec.override_chord_pitches is None:
            prev_chord = previous_episode.bars[-1].chords[-1]
            cnro, next_pitches = NROUtils.get_random_admissible_cnro(prev_chord.pitches,
                                                                     spec.min_cnro_length,
                                                                     spec.max_cnro_length,
                                                                     spec.fixed_key_sig,
                                                                     spec.majmin_constraint)
        if next_pitches is None:
            next_pitches = ChordUtils.get_suitable_chord_pitches(spec.fixed_key_sig, spec.majmin_constraint, spec.focal_pitch)
        num_reps = 1
        for bar_ind, bar in enumerate(this_episode.bars):
            spec = SpecUtils.get_instantiated_copy(self.chord_sequence_gen_spec, bar)
            if spec.override_chord_pitches is not None:
                next_pitches = [int(i) for i in spec.override_chord_pitches.split(",")]
            next_pitches = ChordUtils.mapped_to_focal_pitch(next_pitches, spec.focal_pitch)
            next_pitches.sort()
            for chord_ind, chord in enumerate(bar.chords):
                chord.pitches = next_pitches
                chord.chord_name = ChordUtils.get_chord_name(chord)
                cnro, new_pitches = NROUtils.get_random_admissible_cnro(chord.pitches, spec.min_cnro_length, spec.max_cnro_length,
                                                                        spec.fixed_key_sig, spec.majmin_constraint)
                if self.chord_sequence_gen_spec.max_repetitions is not None and num_reps == self.chord_sequence_gen_spec.max_repetitions:
                    while ChordUtils.are_same_pitch_classes(chord.pitches, new_pitches):
                        cnro, new_pitches = NROUtils.get_random_admissible_cnro(chord.pitches, spec.min_cnro_length,
                                                                                spec.max_cnro_length, spec.fixed_key_sig,
                                                                                spec.majmin_constraint)
                num_reps = 1 if not ChordUtils.are_same_pitch_classes(chord.pitches, new_pitches) else num_reps + 1
                if spec.focal_pitch is not None:
                    new_pitches = ChordUtils.mapped_to_focal_pitch(new_pitches, spec.focal_pitch)
                new_pitches.sort()
                next_pitches = new_pitches
