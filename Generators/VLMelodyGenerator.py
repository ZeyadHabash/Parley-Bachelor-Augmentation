from Parley.Utils.MelodyUtils import *
from Parley.Utils.VolumeUtils import *
from Parley.Utils.RhythmUtils import *
from Parley.Utils.SpecUtils import *


class VLMelodyGenerator:

    def __init__(self, note_sequence_gen_spec):
        self.note_sequence_gen_spec = note_sequence_gen_spec

    def update_note_sequence(self, pass_num, previous_episode, this_episode, next_episode):
        spec = self.note_sequence_gen_spec
        if pass_num == 0:
            self.add_backbone_notes(previous_episode, this_episode)

        if pass_num == 1:
            self.add_passing_notes(this_episode, next_episode)
            RhythmUtils.quantize(this_episode, spec.track_num)
            self.tie_notes_for_rhythm(this_episode, spec.track_num)

        if pass_num == 2:
            self.handle_repetitions(this_episode, next_episode)
            self.add_volumes(this_episode)

    def add_backbone_notes(self, previous_episode, this_episode):
        target_start_pitch = None
        if previous_episode is not None:
            matching_note_sequence = self.get_matching_note_sequence(previous_episode.bars[-1])
            if matching_note_sequence is not None:
                target_start_pitch = matching_note_sequence.notes[-1].pitch
        for bar in this_episode.bars:
            spec = SpecUtils.get_instantiated_copy(self.note_sequence_gen_spec, bar)
            allow_target_pitch = False if spec.repetition_policy == "disallow" else True
            num_backbone_notes = spec.backbone_length
            if bar.note_sequences is None:
                bar.note_sequences = []
            num_backbone_notes_hash = {}
            total = 0
            for chord in bar.chords:
                frac = chord.duration_ticks/bar.duration_ticks
                num_backbone_notes_for_chord = int(round(frac * num_backbone_notes))
                num_backbone_notes_hash[chord] = num_backbone_notes_for_chord
                total += num_backbone_notes_for_chord
            while total < num_backbone_notes:
                num_backbone_notes_hash[random.choice(bar.chords)] += 1
                total += 1
            while total > num_backbone_notes:
                num_backbone_notes_hash[random.choice(bar.chords)] -= 1
                total -= 1
            notes = []
            for chord in bar.chords:
                num_backbone_notes_for_chord = max(1, num_backbone_notes_hash[chord])
                backbone_sequences = MelodyUtils.get_backbone_sequences(chord, num_backbone_notes_for_chord, spec.octave_offset)
                backbone_sequence = MelodyUtils.random_from_top_bracket(backbone_sequences, target_start_pitch, allow_target_pitch)
                note_duration_ticks = int(round(chord.duration_ticks/len(backbone_sequence)))
                start_tick = bar.start_tick
                for ind, pitch in enumerate(backbone_sequence):
                    moved_pitch = pitch
                    note = Note(pitch=moved_pitch, volume=127, start_tick=start_tick,
                                duration_ticks=note_duration_ticks, cutoff_prop=1, tied_duration_ticks=None,
                                parent_chord=chord, parent_bar=bar, parent_note_sequence=None,
                                tie_type=None, is_backbone_note=True,
                                is_backbone_starter=(ind==0), num_fracs=None, score_colour=None,
                                interestingness_profile=None, edit_improvement=None, edit_index=None,
                                score_notes=[])
                    notes.append(note)
                    start_tick += note_duration_ticks
                target_start_pitch = backbone_sequence[-1]
            note_sequence = NoteSequence(spec.id, spec.track_num, spec.channel_num, spec.instrument_num, notes, None, parent_bar=bar)
            for note in note_sequence.notes:
                note.parent_note_sequence = note_sequence
            bar.note_sequences.append(note_sequence)

    def add_passing_notes(self, this_episode, next_episode):
        next_note_hash = self.get_next_note_hash(this_episode, next_episode)
        for bar_ind, bar in enumerate(this_episode.bars):
            spec = SpecUtils.get_instantiated_copy(self.note_sequence_gen_spec, bar)
            if spec.passing_notes_policy == "all" or spec.passing_notes_policy == "mid":
                total_chord_duration = 0
                for chord in bar.chords:
                    total_chord_duration += chord.duration_ticks
                total_notes_duration = 0
                note_sequence = self.get_matching_note_sequence(bar)
                new_notes = []
                for note in note_sequence.notes:
                    next_note = next_note_hash[note]
                    if next_note is not None:
                        target_pitch = next_note_hash[note].pitch
                        passing_note_pitches = MelodyUtils.get_passing_note_pitches(note, target_pitch,
                                                                                    spec.fixed_key_sig, spec.passing_notes_policy)
                        duration_ticks = int(note.duration_ticks/len(passing_note_pitches))
                        for ind, pitch in enumerate(passing_note_pitches):
                            start_tick = next_note.start_tick + (ind * duration_ticks)
                            new_note = Note(pitch=pitch, volume=127, start_tick=start_tick,
                                            duration_ticks=duration_ticks,
                                            tied_duration_ticks=None, cutoff_prop=1,
                                            parent_chord=note.parent_chord, parent_bar=bar,
                                            parent_note_sequence=note_sequence,
                                            tie_type=None, is_backbone_note=(pitch == note.pitch),
                                            is_backbone_starter=(pitch == note.pitch and note.is_backbone_starter),
                                            start_frac=None, num_fracs=None, edit_improvement=None, edit_index=None,
                                            score_chord_name=None, score_notes=[])
                            new_notes.append(new_note)
                            total_notes_duration += duration_ticks
                    else:
                        new_notes.append(note)
                direction = 1 if total_notes_duration <= total_chord_duration else -1

                while total_notes_duration != total_chord_duration:
                    note = random.choice(new_notes)
                    note.duration_ticks += direction
                    total_notes_duration += direction
                new_note_sequence = NoteSequence(spec.id, spec.track_num, spec.channel_num,
                                                 spec.instrument_num, new_notes, None, parent_bar=bar)
                bar.note_sequences.remove(note_sequence)
                bar.note_sequences.append(new_note_sequence)

    def get_next_note_hash(self, this_episode, next_episode):
        note_next_hash = {}
        for bar_ind, bar in enumerate(this_episode.bars):
            note_sequence = self.get_matching_note_sequence(bar)
            for note_ind, note in enumerate(note_sequence.notes):
                if note_ind < (len(note_sequence.notes) - 1):
                    note_next_hash[note] = note_sequence.notes[note_ind + 1]
                else:
                    if bar_ind < (len(this_episode.bars) - 1):
                        matching_note_sequence = self.get_matching_note_sequence(this_episode.bars[bar_ind + 1])
                        note_next_hash[note] = matching_note_sequence.notes[0]
                    elif next_episode is not None:
                        matching_note_sequence = self.get_matching_note_sequence(next_episode.bars[0])
                        note_next_hash[note] = matching_note_sequence.notes[0]
                    else:
                        note_next_hash[note] = None
        return note_next_hash

    def get_matching_note_sequence(self, bar):
        for note_sequence in bar.note_sequences:
            if note_sequence.track_num == self.note_sequence_gen_spec.track_num:
                return note_sequence
        return None

    def tie_notes_for_rhythm(self, episode, track_num):
        for bar in episode.bars:
            for note_sequence in bar.note_sequences:
                if note_sequence.track_num == track_num:
                    new_notes = []
                    for note in note_sequence.notes:
                        q_split = RhythmUtils.get_note_quantization_split(note.num_fracs)
                        first_note = note.__copy__()
                        new_notes.append(first_note)
                        if len(q_split) > 1:
                            first_note.tied_duration_ticks = first_note.duration_ticks
                            first_note.num_fracs = q_split[0][0]
                            f = first_note.num_fracs/128
                            first_note.duration_ticks = int(round(bar.duration_ticks * f))
                            first_note.tie_type = "start"
                            start_frac = first_note.start_frac + first_note.num_fracs
                            for q_ind, qs in enumerate(q_split[1:]):
                                tied_note = note.__copy__()
                                tied_note.start_frac = start_frac
                                tied_note.num_fracs = qs[0]
                                start_frac += tied_note.num_fracs
                                tied_note.tied_duration_ticks = 0
                                f = tied_note.num_fracs/128
                                tied_note.duration_ticks = int(round(bar.duration_ticks * f))
                                tied_note.tie_type = "end" if q_ind == len(q_split) - 2 else "mid"
                                new_notes.append(tied_note)
                    note_sequence.notes = new_notes

    def handle_repetitions(self, this_episode, next_episode):
        next_note_hash = self.get_next_note_hash(this_episode, next_episode)
        for note in next_note_hash.keys():
            if note.tie_type is None:
                repeated_notes = []
                next_note = next_note_hash[note]
                total_tied_duration_ticks = note.duration_ticks
                while next_note is not None and next_note.pitch == note.pitch:
                    repeated_notes.append(next_note)
                    total_tied_duration_ticks += next_note.duration_ticks
                    next_note = None if next_note not in next_note_hash else next_note_hash[next_note]
                if len(repeated_notes) > 0:
                    spec = SpecUtils.get_instantiated_copy(self.note_sequence_gen_spec, note.parent_bar)
                    if spec.repetition_policy == "staccato":
                        note.cutoff_prop = 0.5
                        for n in repeated_notes:
                            n.cutoff_prop = 0.5
                    if spec.repetition_policy == "rest":
                        note.pitch = None
                    if spec.repetition_policy == "tie" and note.tie_type is None:
                        note.tie_type = "start"
                        note.tied_duration_ticks = total_tied_duration_ticks
                        repeated_notes[-1].tie_type = "end"
                        for tied_note in repeated_notes:
                            if tied_note.tie_type != "end":
                                tied_note.tie_type = "mid"

    def add_volumes(self, this_episode):
        VolumeUtils.update_volumes(this_episode, self.note_sequence_gen_spec)
