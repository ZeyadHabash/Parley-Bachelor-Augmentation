from Parley.Utils.ExtractionUtils import *
from Parley.Utils.RhythmUtils import *


class SimplifyingTiedNoteEditor:

    def __init__(self, edit_spec):
        self.edit_spec = edit_spec

    def simplify_track(self, composition, track_num):

        # Join together tied notes in a bar

        notes = ExtractionUtils.get_track_notes_for_composition(composition)[track_num]
        notes_to_remove = []
        for ind, note in enumerate(notes):
            note_is_at_start_of_bar = (note.start_tick == note.parent_bar.start_tick)
            if note.tie_type == "start" or (note.tie_type == "mid" and note_is_at_start_of_bar):
                next_note = None if note == notes[-1] else notes[ind + 1]
                i = ind + 1
                while next_note is not None and next_note.parent_bar == note.parent_bar:
                    if next_note.tie_type == "mid" or next_note.tie_type == "end":
                        if next_note.tie_type == "end":
                            note.tie_type = None if note.tie_type == "start" else "end"
                            note.tied_duration_ticks = None
                        notes_to_remove.append(next_note)
                        note.duration_ticks += next_note.duration_ticks
                        note.num_fracs += next_note.num_fracs
                        i += 1
                        next_note = None if i == len(notes) else notes[i]
                    else:
                        next_note = None

        # Remove notes which have been lost through removing the tie

        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num == track_num:
                        new_notes = []
                        for note in note_sequence.notes:
                            if note not in notes_to_remove:
                                new_notes.append(note)
                        note_sequence.notes = new_notes

        # Split awkward fractions into two or more notes

        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num == track_num:
                        new_notes = []
                        for note in note_sequence.notes:
                            new_notes.append(note)
                            dur_dot_pairs = RhythmUtils.get_note_quantization_split(note.num_fracs)
                            if len(dur_dot_pairs) > 1:
                                dur_dot_pairs = RhythmUtils.get_best_beat_ordering(dur_dot_pairs, note.start_frac)
                            if len(dur_dot_pairs) > 1:
                                if bar.comp_bar_num == 89:
                                    print(note.num_fracs, dur_dot_pairs)
                                original_tie_type = note.tie_type
                                dot_mult = 1
                                if dur_dot_pairs[0][1] == 1:
                                    dot_mult = 1.5
                                elif dur_dot_pairs[0][1] == 2:
                                    dot_mult = 1.75
                                note.num_fracs = int(dur_dot_pairs[0][0] * dot_mult)
                                if bar.comp_bar_num == 89:
                                    print(note.num_fracs, dur_dot_pairs)
                                if original_tie_type is None:
                                    note.tie_type = "start"
                                if original_tie_type == "end":
                                    note.tie_type = "mid"
                                note.tied_duration_ticks = note.duration_ticks if original_tie_type is None else note.tied_duration_ticks
                                bar_duration_ticks = note.parent_bar.duration_ticks
                                note.duration_ticks = int(round((note.num_fracs/128) * bar_duration_ticks))
                                frac_ind = 1
                                start_tick = note.start_tick + note.duration_ticks
                                start_frac = note.start_frac + note.num_fracs
                                for num_fracs, num_dots in dur_dot_pairs[1:]:
                                    new_note = note.__copy__()
                                    note.duration_ticks = int(round((num_fracs/128) * bar_duration_ticks))
                                    new_note.start_tick = start_tick
                                    new_note.start_frac = start_frac
                                    dot_mult = 1
                                    if num_dots == 1:
                                        dot_mult = 1.5
                                    elif num_dots == 2:
                                        dot_mult = 1.75
                                    new_note.num_fracs = int(num_fracs * dot_mult)
                                    if bar.comp_bar_num == 89:
                                        print(num_fracs, dur_dot_pairs, new_note.num_fracs)
                                    if frac_ind < len(dur_dot_pairs) - 1:
                                        new_note.tie_type = "mid"
                                    else:
                                        if original_tie_type is None or original_tie_type == "end":
                                            new_note.tie_type = "end"
                                        elif original_tie_type == "mid" or original_tie_type == "start":
                                            new_note.tie_type = "mid"

                                    new_notes.append(new_note)
                                    frac_ind += 1
                                    start_tick += new_note.duration_ticks
                                    start_frac += new_note.num_fracs
                                if bar.comp_bar_num == 4 and note_sequence.track_num == 4:
                                    for n in new_notes:
                                        print(n.tie_type)
                                    print("---")
                        note_sequence.notes = new_notes


