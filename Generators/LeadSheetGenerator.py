from copy import deepcopy
from Parley.Utils.IOUtils import *


class LeadSheetGenerator:

    def __init__(self, gen_spec):
        self.gen_spec = gen_spec

    def generate_lead_sheet(self, form, composition_gen_spec):
        lead_sheet_form = deepcopy(form)
        for episode in lead_sheet_form.episodes:
            for bar in episode.bars:
                bar.note_sequences = []
                for i in range(0, 4):
                    notes = []
                    start_tick = 0
                    start_frac = 0
                    for chord in bar.chords:
                        num_fracs = int((chord.num_fracs/chord.frac) * 128)
                        pitch = chord.pitches[0] + 12 if i == 3 else chord.pitches[i] - 12
                        score_chord_name = chord.chord_name if i == 0 else None
                        note = Note(pitch=pitch, volume=100, start_tick=start_tick, duration_ticks=chord.duration_ticks,
                                    cutoff_prop=1, tied_duration_ticks=None,
                                    parent_chord=chord, parent_bar=bar, parent_note_sequence=None, tie_type=None,
                                    is_backbone_note=None, is_backbone_starter=None, start_frac=start_frac, num_fracs=num_fracs,
                                    score_colour=None, interestingness_profile=None, edit_improvement=None, edit_index=None,
                                    score_chord_name=score_chord_name, score_notes=[])
                        notes.append(note)
                        start_tick += chord.duration_ticks
                        start_frac += num_fracs
                    note_sequence = NoteSequence(id="", track_num=i, channel_num=i, instrument_num=0, notes=notes, parent_bar=bar)
                    bar.note_sequences.append(note_sequence)
        lead_sheet_composition = Composition(composition_gen_spec.title + " - Lead Sheet", lead_sheet_form)
        part_gen_specs = [ScorePartGenSpec("Piano", "Piano", [("treble", [3]), ("bass", [0, 1, 2])])]
        cgs = deepcopy(composition_gen_spec)
        cgs.score_gen_spec = ScoreGenSpec(lead_sheet_composition.title, part_gen_specs, True, True, True)
        cgs.output_stem = composition_gen_spec.output_stem + "_ls"
        return lead_sheet_composition, cgs