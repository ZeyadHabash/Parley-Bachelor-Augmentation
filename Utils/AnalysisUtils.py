from Parley.Utils.ExtractionUtils import *
from Parley.Utils.ChordUtils import *
from Parley.Utils.DataUtils import *
from dataclasses import dataclass
from Parley.Editors.DiscordanceEditor import *
from Parley.Specifications.Specifications import *


@dataclass
class MusicalAnalysis:
    interval_details: AnalysisClass
    pitch_class_details: AnalysisClass
    run_length_details: AnalysisClass
    voice_leading_details: AnalysisClass
    bn_chord_match_details: AnalysisClass
    pn_chord_match_details: AnalysisClass
    edit_improvement_details: AnalysisClass
    discordance_details: AnalysisClass

class AnalysisUtils:

    def get_musical_analysis(composition, track_num):
        notes = ExtractionUtils.get_track_notes_for_composition(composition)[track_num]
        notes = [n for n in notes if (n.tie_type is None or n.tie_type == "start")]
        return AnalysisUtils.get_musical_analysis_for_notes(composition, notes, track_num)

    def get_musical_analysis_for_notes(composition, notes, track_num):
        interval_details = AnalysisUtils.get_interval_details(notes)
        pitch_class_details = AnalysisUtils.get_pitch_class_details(notes)
        run_length_details = AnalysisUtils.get_run_length_details(notes)
        voice_leading_details = AnalysisUtils.get_voice_leading_details(notes)
        bn_chord_match_details = AnalysisUtils.get_bn_chord_match_details(notes)
        pn_chord_match_details = AnalysisUtils.get_pn_chord_match_details(notes)
        edit_improvement_details = AnalysisUtils.get_edit_improvement_details(notes)
        discordance_details = AnalysisUtils.get_discordance_details(composition, notes, track_num)
        return MusicalAnalysis(interval_details, pitch_class_details, run_length_details,
                               voice_leading_details, bn_chord_match_details,
                               pn_chord_match_details, edit_improvement_details,
                               discordance_details)

    def get_interval_details(notes):
        intervals = [ChordUtils.get_interval(notes[i-1].pitch, notes[i].pitch) for i in range(1, len(notes))]
        return DataUtils.get_analysis_details(intervals)

    def get_pitch_class_details(notes):
        pitch_classes = [ChordUtils.pitch_class(note.pitch) for note in notes]
        return DataUtils.get_analysis_details(pitch_classes)

    def get_run_length_details(notes):
        run_lengths = []
        previous_direction = 1 if notes[1].pitch > notes[0].pitch else (-1 if notes[1].pitch < notes[0].pitch else 0)
        run_length = 2
        for i in range(1, len(notes)):
            direction = 1 if notes[i].pitch > notes[i-1].pitch else (-1 if notes[i].pitch < notes[i-1].pitch else 0)
            if direction == previous_direction:
                run_length += 1
            else:
                run_lengths.append(run_length)
                run_length = 2
            previous_direction = direction
        return DataUtils.get_analysis_details(run_lengths)

    def get_voice_leading_details(notes):
        vl_scores = []
        for i in range(1, len(notes)):
            score = 1 if abs(notes[i].pitch - notes[i-1].pitch) <= 2 else 0
            vl_scores.append(score)
        return DataUtils.get_analysis_details(vl_scores)

    def get_bn_chord_match_details(notes):
        chord_match_scores = []
        for note in [n for n in notes if n.is_backbone_note]:
            chord_pitches = [ChordUtils.pitch_class(c) for c in note.parent_chord.pitches]
            cm_score = 1 if ChordUtils.pitch_class(note.pitch) in chord_pitches else 0
            chord_match_scores.append(cm_score)
        return DataUtils.get_analysis_details(chord_match_scores)

    def get_pn_chord_match_details(notes):
        chord_match_scores = []
        for note in [n for n in notes if not n.is_backbone_note]:
            chord_pitches = [ChordUtils.pitch_class(c) for c in note.parent_chord.pitches]
            cm_score = 1 if ChordUtils.pitch_class(note.pitch) in chord_pitches else 0
            chord_match_scores.append(cm_score)
        return DataUtils.get_analysis_details(chord_match_scores)

    def get_edit_improvement_details(notes):
        edit_improvement_scores = []
        for note in notes:
            if note.edit_improvement is not None:
                edit_improvement_scores.append(note.edit_improvement)
        return DataUtils.get_analysis_details(edit_improvement_scores)

    def get_discordance_details(composition, notes, track_num):
        edit_spec = DiscordanceEditSpec(interval_scores={1: -2, 11: -1}, score_threshold=-2,
                                        duration_ticks_threshold=400, ignore_passing_notes=True,
                                        tracks_to_edit=[track_num], edit_technique="alter")
        discordance_editor = DiscordanceEditor(edit_spec, composition)
        dhash = discordance_editor.discordances_hash
        discordance_counts = []
        for note in notes:
            count = 0 if note not in dhash else len(dhash[note])
            discordance_counts.append(count)
        return DataUtils.get_analysis_details(discordance_counts)