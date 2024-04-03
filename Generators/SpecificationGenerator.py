from Parley.Specifications.InstrumentNums import *
from Parley.Specifications.GeneratorStructure import *
from Parley.Utils.ScoreUtils import *
from Parley.Utils.IOUtils import *
import random


class SpecificationGenerator:

    def get_composition_spec(self, milliseconds_duration):
        num_episodes = random.randint(1, 5)
        fixed_key_sig = random.choice([None, "cmaj", "gmaj", "fmaj"])
        episode_specs = []
        chord_instrument_num = random.randint(0, SFEssential.num_instruments - 1)
        melody_instrument_num = random.randint(0, SFEssential.num_instruments - 1)
        majmin_type_num = random.randint(0, 4)
        for episode_num in range(0, num_episodes):
            bar_structure_gen_spec = self.get_bar_structure_gen_spec(milliseconds_duration, num_episodes)
            chord_sequence_gen_spec = self.get_chord_sequence_gen_spec(episode_num, majmin_type_num, fixed_key_sig)
            note_sequence_gen_specs = []
            for chord_note_num in range(1, 4):
                note_sequence = self.get_chord_note_sequence(chord_note_num - 1, chord_note_num, fixed_key_sig, chord_instrument_num)
                note_sequence_gen_specs.append(note_sequence)
            vl_melody_note_sequence = self.get_vl_nelody_note_sequence(episode_num, 3, melody_instrument_num, fixed_key_sig)
            note_sequence_gen_specs.append(vl_melody_note_sequence)
            episode_gen_spec = EpisodeGenSpec(bar_structure_gen_spec, chord_sequence_gen_spec, note_sequence_gen_specs)
            episode_specs.append(episode_gen_spec)

        form_gen_spec = FormGenSpec(episode_specs)
        melody_score_part_gen_spec = ScorePartGenSpec("Melody", "Melody", [("treble", [3])])
        chords_score_part_gen_spec = ScorePartGenSpec("Chords", "Chords", [("bass", [0, 1, 2])])
        score_gen_spec = [melody_score_part_gen_spec, chords_score_part_gen_spec]
        return CompositionGenSpec(form_gen_spec), score_gen_spec

    def get_bar_structure_gen_spec(self, milliseconds_duration, num_episodes):
        episode_duration_ms = int(milliseconds_duration/num_episodes)
        bar_start_target_duration_ms = 2000
        bar_end_target_duration_ms = 2000
        speed_change_r = random.randint(0, 2)
        if speed_change_r == 0:
            bar_start_target_duration_ms = int(random.uniform(0.8, 1) * bar_start_target_duration_ms)
            bar_end_target_duration_ms = int(random.uniform(1, 1.2) * bar_end_target_duration_ms)
        if speed_change_r == 1:
            bar_start_target_duration_ms = int(random.uniform(1, 1.2) * bar_start_target_duration_ms)
            bar_end_target_duration_ms = int(random.uniform(0.8, 1.0) * bar_end_target_duration_ms)
        bar_structure_gen_spec = BarStructureGenSpec(episode_target_duration_ms=episode_duration_ms,
                                                     bar_start_target_duration_ms=bar_start_target_duration_ms,
                                                     bar_end_target_duration_ms=bar_end_target_duration_ms,
                                                     rhythm="1:1/1:1/1")
        return bar_structure_gen_spec

    def get_chord_sequence_gen_spec(self, episode_num, majmin_type_num, fixed_key_sig):
        alt = "maj" if episode_num % 2 == 0 else "min"
        majmin_options = [None, "maj", "min", "majmin", alt]
        majmin_constraint = majmin_options[majmin_type_num]
        print(majmin_constraint)
        chord_sequence_gen_spec = NRTChordSequenceGenSpec(override_chord_pitches="69,72,76(cb=0,cb=-1)", focal_pitch=70,
                                                          fixed_key_sig=fixed_key_sig, inherit_fixed_key=False,
                                                          start_nro=None, min_cnro_length=1, max_cnro_length=1,
                                                          is_classic=False, majmin_constraint=majmin_constraint)
        return chord_sequence_gen_spec

    def get_chord_note_sequence(self, track_num, chord_note, fixed_key_sig, instrument_num):
        note_sequence_gen_spec = RhythmGenSpec(id="chord_lower", track_num=track_num,
                                               instrument_num=instrument_num,
                                               volume=60, octave_offset=-1,
                                               rhythm=f"{chord_note}:1/1:1/1",
                                               fixed_key_sig=fixed_key_sig)
        return note_sequence_gen_spec

    def get_vl_nelody_note_sequence(self, episode_num, track_num, instrument_num, fixed_key_sig):
        passing_notes_policy = "all(pc=60) mid(pc=30) none(pc=10)"
        repetition_policy = "disallow(pc=10) allow(pc=10) staccato(pc=10) tie(pc=70)"
        note_sequence_gen_spec = VLMelodyGenSpec(id="melody", track_num=track_num, instrument_num=instrument_num,
                                                 volume=80, octave_offset=0,
                                                 backbone_length="3(pc=50) 4(pc=50)",
                                                 fixed_key_sig=fixed_key_sig,
                                                 note_length=1, passing_notes_policy=passing_notes_policy,
                                                 repetition_policy=repetition_policy)
        return note_sequence_gen_spec


fixed_seed = None
#fixed_seed = 23173
seed = fixed_seed if fixed_seed is not None else random.randint(0, 100000)
random.seed(seed)
print("Seed:", seed)

spec_generator = SpecificationGenerator()
composition_gen_spec, score_gen_spec = spec_generator.get_composition_spec(60000)
#print(SpecUtils.spec_string(composition_gen_spec))

composition_generator = CompositionGenerator(composition_gen_spec)
composition = composition_generator.generate_composition(seed)

output_dir = "./outputs/inventions"
soundfont_filepath = InstrumentNums.SFEssential.soundfont_filepath
stem = f"../outputs/inventions/invention_{seed}"
IOUtils.save_all_aspects(composition=composition,
                         title="Invention",
                         soundfont_filepath=soundfont_filepath,
                         output_dir=output_dir,
                         stem=stem, seed=seed,
                         part_specs=score_gen_spec,
                         show_colours=True,
                         show_bar_tag=True)



