from Parley.Specifications.InstrumentNums import *
from Parley.Specifications.GeneratorStructure import *
from Parley.Utils.IOUtils import *
from Parley.Utils.SpecUtils import *
from Parley.Utils.SoundfontUtils import *


class ExcerptGenerator:

    def __init__(self, gen_spec):
        self.gen_spec = gen_spec

    def get_excerpt_gen_spec(self, output_stem, include_percussion):
        episode_specs = []
        bar_structure_gen_spec = self.get_bar_structure_gen_spec()
        chord_sequence_gen_spec, fixed_key_sig = self.get_chord_sequence_gen_spec()
        note_sequence_gen_specs = self.get_chord_note_sequence_gen_specs(fixed_key_sig)
        note_sequence_gen_specs.append(self.get_vl_melody_note_sequence_gen_spec(fixed_key_sig))
        if include_percussion:
            note_sequence_gen_specs.extend(self.get_percussion_note_sequence_gen_spec())
        episode_gen_spec = EpisodeGenSpec(bar_structure_gen_spec, chord_sequence_gen_spec, note_sequence_gen_specs)
        episode_specs.append(episode_gen_spec)
        form_gen_spec = FormGenSpec(episode_specs)
        melody_inst_num = note_sequence_gen_specs[3].instrument_num
        chord_inst_num = note_sequence_gen_specs[0].instrument_num
        melody_inst_name, _ = SoundfontUtils.get_instrument_name_and_type("SFFluidSynth", melody_inst_num)
        chord_inst_name, _ = SoundfontUtils.get_instrument_name_and_type("SFFluidSynth", chord_inst_num)
        melody_score_part_gen_spec = ScorePartGenSpec("Melody", melody_inst_name, [("treble", [3])])
        chords_score_part_gen_spec = ScorePartGenSpec("Chords", chord_inst_name, [("bass", [0, 1, 2])])
        score_gen_spec = ScoreGenSpec(part_gen_specs=[melody_score_part_gen_spec, chords_score_part_gen_spec],
                                      show_colours=True, show_bar_tag=True)
        seed = random.randint(0, 1000000)
        return CompositionGenSpec("Excerpt", seed, output_stem, form_gen_spec, None, score_gen_spec, self.gen_spec.midi_gen_spec)

    def get_bar_structure_gen_spec(self):
        bar_target_duration_ms = random.randint(1500, 3000)
        rhythms = ["1:1/1:1/1", "1:1/2:1/2,1:2/2:1/2"]
        bar_structure_gen_spec = BarStructureGenSpec(episode_target_duration_ms=bar_target_duration_ms * 4,
                                                     bar_start_target_duration_ms=bar_target_duration_ms,
                                                     bar_end_target_duration_ms=bar_target_duration_ms,
                                                     rhythm=random.choice(rhythms))
        return bar_structure_gen_spec

    def get_chord_sequence_gen_spec(self):
        majmin_constraint = random.choice([None, "maj", "min", "majmin"])
        fixed_key_sig = random.choice([None, "cmaj", "amin"])
        focal_pitch = random.randint(60, 72)
        min_cnro_length = random.randint(1, 3)
        max_cnro_length = min_cnro_length + random.randint(0, 1)
        chord_sequence_gen_spec = NRTChordSequenceGenSpec(override_chord_pitches=None, focal_pitch=focal_pitch,
                                                          fixed_key_sig=fixed_key_sig,
                                                          start_nro=None, min_cnro_length=min_cnro_length,
                                                          max_cnro_length=max_cnro_length,
                                                          is_classic=False, majmin_constraint=majmin_constraint)
        return chord_sequence_gen_spec, fixed_key_sig

    def get_chord_note_sequence_gen_specs(self, fixed_key_sig):
        chord_note_sequence_gen_specs = []
        ids = ["chord_lower", "chord_mid", "chord_upper"]
        instrument_num = SoundfontUtils.get_random_instrument_num("SFFluidSynth", self.gen_spec.chord_instrument_types)
        rhythm_pos = random.randint(0, 1)
        octave_offset = random.randint(-2, -1)
        volume = random.randint(60, 80)
        for i in range(0, 3):
            rhythms = [f"{i+1}:1/1:1/1", f"{i+1}:1/2:1/2,{i+1}:2/2:1/2"]
            note_sequence_gen_spec = RhythmGenSpec(id=ids[i], track_num=i, channel_num=i,
                                                   instrument_num=instrument_num,
                                                   volume=volume, octave_offset=octave_offset,
                                                   rhythm=rhythms[rhythm_pos],
                                                   fixed_key_sig=fixed_key_sig)
            chord_note_sequence_gen_specs.append(note_sequence_gen_spec)
        return chord_note_sequence_gen_specs

    def get_vl_melody_note_sequence_gen_spec(self, fixed_key_sig):
        passing_notes_policy = random.choice(["all", "mid", "none"])
        repetition_policy = random.choice(["disallow", "allow", "staccato", "tie"])
        instrument_num = SoundfontUtils.get_random_instrument_num("SFFluidSynth", self.gen_spec.melody_instrument_types)
        backbone_length = random.randint(1, 6)
        octave_offset = random.randint(0, 2)
        volume = random.randint(80, 100)
        note_sequence_gen_spec = VLMelodyGenSpec(id="melody", track_num=3, channel_num=3,
                                                 instrument_num=instrument_num,
                                                 volume=volume, octave_offset=octave_offset,
                                                 backbone_length=backbone_length,
                                                 fixed_key_sig=fixed_key_sig,
                                                 note_length=1, passing_notes_policy=passing_notes_policy,
                                                 repetition_policy=repetition_policy)
        return note_sequence_gen_spec

    def get_percussion_note_sequence_gen_spec(self):
        percussion_note_sequence_gen_specs = []
        ids = ["percussion1", "percussion2"]
        octave_offset = random.randint(-2, -1)
        volume = random.randint(50, 70)
        for i in range(0, 2):
            instrument_num = random.randint(27, 87)
            rhythms = ["1:1/1:1/1", "1:1/2:1/2,1:2/2:1/2", "1:1/4:1/4,1:2/4:1/4,1:3/4:1/4,1:4/4:1/4",
                       "1:1/8:1/8,1:2/8:1/8,1:3/8:1/8,1:4/8:1/8,1:5/8:1/8,1:6/8:1/8,1:7/8:1/8,1:8/8:1/8"]
            note_sequence_gen_spec = RhythmGenSpec(id=ids[i], track_num=4 + i, channel_num=9,
                                                   instrument_num=instrument_num,
                                                   volume=volume, octave_offset=octave_offset,
                                                   rhythm=random.choice(rhythms),
                                                   fixed_key_sig=None)
            percussion_note_sequence_gen_specs.append(note_sequence_gen_spec)
        return percussion_note_sequence_gen_specs


    def save_excerpts(self, output_dir, composition_gen_spec, num_reps):
        for i in range(0, num_reps):
            composition_generator = CompositionGenerator(composition_gen_spec)
            composition = composition_generator.generate_composition()
            stem = f"{output_dir}/excerpt_{composition_gen_spec.seed}"
            IOUtils.save_all_aspects(composition=composition,
                                     composition_gen_spec=composition_gen_spec,
                                     title="Excerpt", stem=stem)

