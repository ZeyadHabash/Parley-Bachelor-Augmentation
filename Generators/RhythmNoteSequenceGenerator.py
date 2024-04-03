from Parley.Utils.RhythmUtils import *
from Parley.Utils.VolumeUtils import *
from Parley.Utils.SpecUtils import *


class RhythmNoteSequenceGenerator:

    def __init__(self, note_sequence_gen_spec):
        self.note_sequence_gen_spec = note_sequence_gen_spec

    def update_note_sequence(self, pass_num, _previous_episode, this_episode, _next_episode):

        if pass_num != 0:
            return

        for bar in this_episode.bars:
            spec = SpecUtils.get_instantiated_copy(self.note_sequence_gen_spec, bar)
            notes = []
            if bar.note_sequences is None:
                bar.note_sequences = []
            rparts = spec.rhythm.split(":")
            rhythm_string = spec.rhythm if len(rparts) > 1 else bar.rhythm
            rhythm_details = RhythmUtils.get_start_duration_ticks(bar.duration_ticks, rhythm_string)
            if bar.track_divisions_hash is None:
                bar.track_divisions_hash = {}
            num_divisions = RhythmUtils.get_bar_divisions(rhythm_string)
            bar.track_divisions_hash[spec.track_num] = num_divisions
            for ind, [pitch_index, start_tick, duration_ticks, start_frac, num_fracs] in enumerate(rhythm_details):
                chord_tick = 0
                for chord in bar.chords:
                    prev_chord_tick = chord_tick
                    chord_tick += chord.duration_ticks
                    if prev_chord_tick <= start_tick < chord_tick:
                        pitches = chord.pitches
                        break
                if len(rparts) == 1:
                    pitch = pitches[int(spec.rhythm) - 1]
                else:
                    pitch = None if pitch_index == -1 else (pitches[pitch_index - 1] + (spec.octave_offset * 12))
                note_start_tick = bar.start_tick + start_tick
                note = Note(pitch=pitch, volume=127, start_tick=note_start_tick, duration_ticks=duration_ticks, cutoff_prop=1,
                            tied_duration_ticks=None, parent_chord=chord, parent_bar=bar, parent_note_sequence=None,
                            tie_type=None, is_backbone_note=True, is_backbone_starter=(ind == 0),
                            start_frac=start_frac, num_fracs=num_fracs, score_colour=None,
                            interestingness_profile=None, edit_improvement=None, edit_index=None,
                            score_chord_name=None, score_notes=[])
                notes.append(note)
            note_sequence = NoteSequence(spec.id, spec.track_num, spec.channel_num, spec.instrument_num, notes, None, parent_bar=bar)
            RhythmUtils.correct_note_sequence(note_sequence)
            for note in note_sequence.notes:
                note.parent_note_sequence = note_sequence
            bar.note_sequences.append(note_sequence)

        VolumeUtils.update_volumes(this_episode, self.note_sequence_gen_spec)


