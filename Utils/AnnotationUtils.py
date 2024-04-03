from Parley.Utils.ExtractionUtils import *

class AnnotationUtils:

    def annotate_backbone_notes(composition, track_num):
        all_backbone_bars_and_counts = []
        notes = ExtractionUtils.get_all_notes(composition)
        for note in notes:
            if note.parent_note_sequence.track_num == track_num:
                note.score_colour = "green" if note.is_backbone_note else "orange"

        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num == track_num:
                        if len([n for n in note_sequence.notes if not n.is_backbone_note]) == 0:
                            all_backbone_bars_and_counts.append((bar, len(note_sequence.notes)))

        return all_backbone_bars_and_counts