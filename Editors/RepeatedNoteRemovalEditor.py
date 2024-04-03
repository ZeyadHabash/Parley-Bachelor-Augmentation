from Parley.Utils.ExtractionUtils import *


class RepeatedNoteRemovalEditor:

    def __init__(self, edit_spec):
        self.edit_spec = edit_spec

    def remove_repeated_notes(self, composition):
        all_notes_hash = ExtractionUtils.get_track_notes_for_composition(composition)
        for track_num in self.edit_spec.ordered_track_nums:
            all_notes = []
            for other_track_num in self.edit_spec.ordered_track_nums:
                if other_track_num != track_num:
                    all_notes.extend(all_notes_hash[other_track_num])
            for remove_note in all_notes_hash[track_num]:
                for keep_note in all_notes:
                    if self.is_repeated_note(remove_note, keep_note):
                        remove_note.pitch = None

    def is_repeated_note(self, note1, note2):
        if note1.pitch != note2.pitch:
            return False
        if abs(note1.start_tick - note2.start_tick) > 10:
            return False
        if abs(note1.duration_ticks - note2.duration_ticks) > 10:
            return False
        return True

