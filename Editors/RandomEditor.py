from Parley.Utils.ExtractionUtils import *
from Parley.Utils.MelodyUtils import *
from Parley.Utils.ChordUtils import *
from Parley.Utils.SpecUtils import  *
import random


class RandomEditor:

    def __init__(self, edit_spec):
        self.edit_spec = edit_spec

    def edit_episode(self, composition, episode):
        notes_in_track = ExtractionUtils.get_track_notes_for_episode(composition, episode)[self.edit_spec.track_num]
        all_notes_for_track = ExtractionUtils.get_track_notes_for_composition(composition)[self.edit_spec.track_num]
        for ind, note in enumerate(notes_in_track):
            if note.tie_type is None or note.tie_type == "start":
                spec = SpecUtils.get_instantiated_copy(self.edit_spec, note.parent_bar)
                is_ok = False
                while not is_ok:
                    pitch_class = random.randint(0, 11)
                    prev_pitch = None if ind == 0 else notes_in_track[ind-1].pitch
                    next_pitch = None if ind == len(notes_in_track) - 1 else notes_in_track[ind + 1].pitch
                    pitch = MelodyUtils.closest_pitch_to_neighbours_for_pitch_class(note.pitch, pitch_class, prev_pitch, next_pitch)
                    if spec.fixed_key_sig is None or ChordUtils.note_is_in_key(pitch, spec.fixed_key_sig):
                        note.pitch = pitch
                        is_ok = True
            MelodyUtils.homogenise_tied_notes(all_notes_for_track, note)

