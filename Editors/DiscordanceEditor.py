from Parley.Utils.ExtractionUtils import *
from Parley.Utils.RhythmUtils import *
from Parley.Specifications.Artefacts import *
from dataclasses import dataclass


@dataclass
class Discordance:
    note1: Note
    note2: Note
    interval: int
    score: int
    start_together: bool
    ticks_overlap: int
    note_set: []


class DiscordanceEditor:

    def __init__(self, edit_spec, composition):
        self.edit_spec = edit_spec
        self.discordances_hash = {}
        overlapping_note_sets = ExtractionUtils.get_overlapping_note_sets(composition)
        for ind, (start_tick, note_set) in enumerate(overlapping_note_sets):
            for i in range(0, len(note_set)):
                for j in range(i + 1, len(note_set)):
                    note1 = note_set[i]
                    note2 = note_set[j]
                    pitch_distance = abs(note1.pitch - note2.pitch)
                    if pitch_distance in self.edit_spec.interval_scores:
                        start_together = abs(note1.start_tick - note2.start_tick) < 10
                        ticks_overlap = RhythmUtils.get_overlap_ticks(note1, note2)
                        score = self.edit_spec.interval_scores[pitch_distance]
                        self.add_discordance(note1, note2, pitch_distance, start_together, ticks_overlap, score, note_set)
                        self.add_discordance(note2, note1, pitch_distance, start_together, ticks_overlap, score, note_set)

    def add_discordance(self, note1, note2, pitch_distance, start_together, ticks_overlap, score, note_set):
        discordances = [] if note1 not in self.discordances_hash else self.discordances_hash[note1]
        is_there_already = (note1, note2) in [(d.note1, d.note2) for d in discordances]
        if not is_there_already:
            discordances.append(Discordance(note1, note2, pitch_distance, score, start_together, ticks_overlap, note_set))
            self.discordances_hash[note1] = discordances

    def handle_discordances(self, composition, episode):
        notes_for_episode = ExtractionUtils.get_episode_notes(composition, episode)
        talking_points = []
        for note in self.discordances_hash:
            if note in notes_for_episode and note.parent_note_sequence.track_num in self.edit_spec.tracks_to_edit:
                if note.is_backbone_note or not self.edit_spec.ignore_passing_notes:
                    total_score = 0
                    total_ticks_overlap = 0
                    for discordance in self.discordances_hash[note]:
                        total_score += discordance.score
                        total_ticks_overlap += discordance.ticks_overlap
                    if total_score <= self.edit_spec.score_threshold and total_ticks_overlap > self.edit_spec.duration_ticks_threshold:
                        note.score_colour = "red"
                        for d in self.discordances_hash[note]:
                            tp = f"discordance in bar {d.note1.parent_bar.comp_bar_num + 1} is: ", d.note1.pitch, d.note2.pitch, d.note1.parent_note_sequence.track_num, d.note2.parent_note_sequence.track_num, "lasting", total_ticks_overlap, "ticks"
                            talking_points.append(tp)
                            d.note2.score_colour = "red"
        return talking_points
