from Parley.Utils.RhythmUtils import *
from Parley.Utils.ExtractionUtils import *
import random


class RhythmRepetitionEditor:

    def __init__(self, edit_spec):
        self.edit_spec = edit_spec

    def copy_rhythms(self, composition):
        possible_pairs = []
        note_sequences = ExtractionUtils.get_note_sequences_hash(composition)[self.edit_spec.rhythm_track_num]
        for ind1 in range(0, len(note_sequences) - 1):
            if self.note_sequence_is_ok(note_sequences[ind1]):
                signature1 = RhythmUtils.get_backbone_passing_note_signature(note_sequences[ind1])
                for ind2 in range(ind1 + 1, min(len(note_sequences), ind1 + self.edit_spec.num_bars_in_window)):
                    if self.note_sequence_is_ok(note_sequences[ind2]):
                        signature2 = RhythmUtils.get_backbone_passing_note_signature(note_sequences[ind2])
                        if signature1 == signature2 and len(signature2) >= self.edit_spec.min_num_notes_in_rhythm:
                            has_added = False
                            for p_ind, (ns1, ns2) in enumerate(possible_pairs):
                                if ns2 == note_sequences[ind2]:
                                    possible_pairs[p_ind] = (ns1, ns2)
                                    has_added = True
                            if not has_added:
                                possible_pairs.append((note_sequences[ind1], note_sequences[ind2]))
        num_pairs = min(self.edit_spec.max_num_repetitions, len(possible_pairs))
        random.shuffle(possible_pairs)
        chosen_pairs = possible_pairs[0:num_pairs]
        for pair in chosen_pairs:
            RhythmUtils.copy_rhythm_onto(pair[0], pair[1])
            score_note = ScoreNote(f"Repeated rhythm (with bar {pair[0].parent_bar.comp_bar_num + 1})", "grey")
            pair[1].parent_bar.score_notes.append(score_note)
            print(pair[0].parent_bar.comp_bar_num, pair[1].parent_bar.comp_bar_num)

    def note_sequence_is_ok(self, note_sequence):
        if note_sequence.notes[0].tie_type == "mid" or note_sequence.notes[0].tie_type == "end":
            return False
        if note_sequence.notes[-1].tie_type == "mid" or note_sequence.notes[-1].tie_type == "start":
            return False
        return True


