from Parley.Utils.ScoreUtils import *
from Parley.Specifications import *
from Parley.Utils.SoundfontUtils import *
from Parley.Utils.SpecUtils import *


class ExcerptExpanderDesigner:

    def __init__(self, designer_spec):
        self.designer_spec = designer_spec

    def design_composition_spec(self, excerpt_gen_spec):
        melody_inst_num = excerpt_gen_spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs[
            3].instrument_num
        chord_inst_num = excerpt_gen_spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs[
            0].instrument_num
        soundfont_class_name = excerpt_gen_spec.midi_gen_spec.soundfont_class_name
        melody_inst, _ = SoundfontUtils.get_instrument_name_and_type(soundfont_class_name, melody_inst_num)
        chord_inst, _ = SoundfontUtils.get_instrument_name_and_type(soundfont_class_name, chord_inst_num)
        part1 = ScorePartGenSpec("Melody", melody_inst, [("treble", [3])])
        part2 = ScorePartGenSpec("Chords", chord_inst, [("bass", [0, 1, 2])])
        part_gen_specs = [part1, part2]
        composition_gen_spec = CompositionGenSpec()
        composition_gen_spec.form_gen_spec = FormGenSpec()
        composition_gen_spec.form_gen_spec.episode_gen_specs = []
        episode_duration_ms = int(self.designer_spec.composition_duration_ms//self.designer_spec.num_episodes)
        for i in range(0, self.designer_spec.num_episodes):
            episode_gen_spec = self.get_episode_gen_spec(i, excerpt_gen_spec, episode_duration_ms)
            composition_gen_spec.form_gen_spec.episode_gen_specs.append(episode_gen_spec)
        composition_gen_spec.score_gen_spec = ScoreGenSpec(part_gen_specs, True, True)
        composition_gen_spec.midi_gen_spec = SpecUtils.spec_copy(excerpt_gen_spec.midi_gen_spec)
        composition_gen_spec.midi_gen_spec.end_rest_ticks = 3000
        return composition_gen_spec

    def get_episode_gen_spec(self, cycle_num, excerpt_gen_spec, episode_duration_ms):
        episode_gen_spec = SpecUtils.spec_copy(excerpt_gen_spec.form_gen_spec.episode_gen_specs[0])
        tempo_mult_parts = self.designer_spec.tempo_cycle.split(",")
        start_duration_mult = float(tempo_mult_parts[cycle_num % len(tempo_mult_parts)])/100
        end_duration_mult = float(tempo_mult_parts[(cycle_num + 1) % len(tempo_mult_parts)])/100
        episode_gen_spec.bar_structure_gen_spec.bar_start_target_duration_ms *= (1 + start_duration_mult)
        episode_gen_spec.bar_structure_gen_spec.bar_end_target_duration_ms *= (1 + end_duration_mult)
        episode_gen_spec.bar_structure_gen_spec.bar_start_target_duration_ms = int(episode_gen_spec.bar_structure_gen_spec.bar_start_target_duration_ms)
        episode_gen_spec.bar_structure_gen_spec.bar_end_target_duration_ms = int(episode_gen_spec.bar_structure_gen_spec.bar_end_target_duration_ms)
        volume_mult_parts = self.designer_spec.volume_cycle.split(",")
        for ind, note_sequence_gen_spec in enumerate(episode_gen_spec.note_sequence_gen_specs):
            pos1 = cycle_num % len(volume_mult_parts)
            pos2 = (cycle_num + 1) % len(volume_mult_parts)
            start_vol_mult = 1 + (float(volume_mult_parts[pos1])/100)
            end_vol_mult = 1 + (float(volume_mult_parts[pos2])/100)
            start_vol = int(note_sequence_gen_spec.volume * start_vol_mult)
            end_vol = int(note_sequence_gen_spec.volume * end_vol_mult)
            start_vol = max(min(start_vol, 127), 0)
            end_vol = max(min(end_vol, 127), 0)
            note_sequence_gen_spec.volume = f"{start_vol}(ebp=0) {end_vol}(ebp=1)"
        episode_gen_spec.bar_structure_gen_spec.episode_target_duration_ms = episode_duration_ms
        return episode_gen_spec
