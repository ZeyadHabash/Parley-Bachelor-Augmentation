from Parley.Utils.ListeningUtils import *
from Parley.Utils.MelodyUtils import *
from Parley.Utils.SpecUtils import *
from Parley.Utils.ModelUtils import *
from tqdm import tqdm


class InterestingnessEditor:

    def __init__(self, edit_spec):
        self.spec = edit_spec

    def edit_episode(self, listening_model, composition, episode):
        notes_to_edit = self.get_notes_to_edit(composition, episode)
        edited_notes = self.edit_notes(listening_model, composition, episode, notes_to_edit)
        self.handle_repeats(composition, episode, edited_notes)

    def get_notes_to_edit(self, composition, episode):
        lower_target = self.spec.lower_target_interestingness
        upper_target = self.spec.upper_target_interestingness
        notes_to_edit = []
        track_notes_in_episode = ExtractionUtils.get_track_notes_for_episode(composition, episode)[self.spec.track_num]
        for note in track_notes_in_episode:
            if note.pitch is not None:
                bar_interestingness = 0 if note.parent_bar.interestingness_profile is None else note.parent_bar.interestingness_profile["fifty"]
                if self.spec.bar_types_to_change == "all" or bar_interestingness < lower_target or bar_interestingness > upper_target:
                    if (note.tie_type is None or note.tie_type == "start")\
                            and (self.spec.note_types_to_change == "all" or not note.is_backbone_note):
                        interestingness = 0 if note.interestingness_profile is None else note.interestingness_profile["fifty"]
                        if self.spec.note_types_to_change == "all" or interestingness < lower_target or interestingness > upper_target:
                            notes_to_edit.append(note)
        return notes_to_edit

    def edit_notes(self, listening_model, composition, episode, notes_to_edit):
        edited_notes = []
        composition_lead_up_hash = ModelUtils.get_lead_up_notes_hash(composition, episode, self.spec.track_num, 50, True)
        all_notes_for_track = ExtractionUtils.get_track_notes_for_composition(composition)[self.spec.track_num]
        target = (self.spec.lower_target_interestingness + self.spec.upper_target_interestingness) / 2
        if len(notes_to_edit) > 0:
            bar = notes_to_edit[0].parent_bar
            spec = SpecUtils.get_instantiated_copy(self.spec, bar)
        for note in tqdm(notes_to_edit):
            if bar != note.parent_bar:
                bar = note.parent_bar
                spec = SpecUtils.get_instantiated_copy(self.spec, bar)
            ind = all_notes_for_track.index(note)
            previous_pitch = all_notes_for_track[ind - 1].pitch if ind > 0 else None
            next_pitch = all_notes_for_track[ind + 1].pitch if ind < len(all_notes_for_track) - 1 else None
            pcs = []
            for n in composition_lead_up_hash[note]:
                if n.pitch is not None:
                    pcs.append(ChordUtils.pitch_class(n.pitch))
            ordered_pitch_classes = ListeningUtils.increasing_likeliness_ordered_pitch_classes(listening_model, pcs)
            pitch_class_pairs = []
            for pos, pc in enumerate(ordered_pitch_classes):
                interestingness = pos + 1
                i_diff = abs(interestingness - target)
                if note.is_backbone_note and self.spec.chord_notes_fixed:
                    if pc in ChordUtils.pitch_classes_for_chord(note.parent_chord):
                        pitch_class_pairs.append([i_diff, pc])
                else:
                    pitch_class_pairs.append([i_diff, pc])
            pitch_class_pairs.sort()
            has_found = False
            original_pitch_class = ChordUtils.pitch_class(note.pitch)
            pitch_classes = [x[1] for x in pitch_class_pairs]
            for pair_ind, pair in enumerate(pitch_class_pairs):
                edited_pitch_class = pair[1]
                pitch_class_is_ok = True
                if spec.repetition_policy == "disallow":
                    if previous_pitch is not None and edited_pitch_class == ChordUtils.pitch_class(previous_pitch):
                        pitch_class_is_ok = False
                    if next_pitch is not None and edited_pitch_class == ChordUtils.pitch_class(next_pitch):
                        pitch_class_is_ok = False
                if pitch_class_is_ok and not has_found:
                    if spec.pitch_change_choice == "closest_to_original":
                        edited_pitch = MelodyUtils.closest_pitch_for_pitch_class(note.pitch, edited_pitch_class)
                    elif spec.pitch_change_choice == "closest_to_neighbours":
                        edited_pitch = MelodyUtils.closest_pitch_to_neighbours_for_pitch_class(note.pitch, edited_pitch_class,
                                                                                               previous_pitch, next_pitch)
                    elif spec.pitch_change_choice == "focal_pitch":
                        edited_pitch = MelodyUtils.closest_pitch_for_pitch_class(note.pitch, edited_pitch_class)
                        edited_pitch = ChordUtils.map_pitch_to_focal_pitch(edited_pitch, spec.focal_pitch)
                    if spec.fixed_key_sig is None or ChordUtils.note_is_in_key(edited_pitch, spec.fixed_key_sig):
                        note.pitch = edited_pitch
                        new_pitch_class_ind = pair_ind
                        has_found = True
                        edited_notes.append(note)

            if original_pitch_class in pitch_classes:
                note.edit_improvement = original_pitch_class - new_pitch_class_ind
                note.edit_index = new_pitch_class_ind
                original_pitch_class_ind = pitch_classes.index(original_pitch_class)
                if original_pitch_class_ind == new_pitch_class_ind:
                    note.score_colour = "blue"
                elif original_pitch_class_ind < new_pitch_class_ind:
                    note.score_colour = "red"
                else:
                    note.score_colour = "green"
            if note.tie_type == "start":
                MelodyUtils.homogenise_tied_notes(all_notes_for_track, note)

        return edited_notes

    def handle_repeats(self, composition, episode, edited_notes):
        all_notes_for_track = ExtractionUtils.get_track_notes_for_composition(composition)[self.spec.track_num]
        for note in edited_notes:
            ind = all_notes_for_track.index(note)
            prev_note = None if ind == 0 else all_notes_for_track[ind - 1]
            next_note = None if ind == len(all_notes_for_track) - 1 else all_notes_for_track[ind + 1]
            if (prev_note is not None and prev_note.pitch == note.pitch) or (next_note is not None and next_note.pitch == note.pitch):
                spec = SpecUtils.get_instantiated_copy(self.spec, note.parent_bar)
                if spec.repetition_policy == "staccato":
                    self.staccato_edited_note(all_notes_for_track, note)
                if spec.repetition_policy == "tie":
                    self.tie_edited_note(all_notes_for_track, note)

    def staccato_edited_note(self, all_notes_for_track, note):
        neighbourhood = MelodyUtils.get_same_pitch_neighbourhood(all_notes_for_track, note)
        for note in neighbourhood:
            if note.tie_type is None:
                note.cutoff_prop = 0.5

    def tie_edited_note(self, all_notes_for_track, note):
        neighbourhood = MelodyUtils.get_same_pitch_neighbourhood(all_notes_for_track, note)
        total_tied_duration_ticks = 0
        for note in neighbourhood:
            note.cutoff_prop = 1
            note.tie_type = "mid"
            note.tied_duration_ticks = None
            total_tied_duration_ticks += note.duration_ticks
        neighbourhood[0].tie_type = "start"
        neighbourhood[0].tied_duration_ticks = total_tied_duration_ticks
        neighbourhood[-1].tie_type = "end"
