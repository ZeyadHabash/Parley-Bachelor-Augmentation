from Parley.InstrumentNums import *
from Parley.GeneratorStructure import *
from Parley.Generators.MidiGenerator import *
from Parley.Generators.AudioGenerator import *
from Parley.Generators.ScoreGenerator import *
from Parley.Utils.ScoreUtils import *
from Parley.Utils.IOUtils import *
from Parley.Editors.InterestingnessEditor import *
from Parley.Editors.DiscordanceEditor import *

class EchoChamber:

    def __init__(self, soundfont_class_name, soundfont_filepath, output_dir, fixed_seed=None):
        self.soundfont_class_name = soundfont_class_name
        self.soundfont_filepath = soundfont_filepath
        self.output_dir = output_dir
        self.fixed_seed = fixed_seed
        self.composition_gen_spec = None
        self.seed = None
        self.composition = None
        self.midi_generator = MidiGenerator(soundfont_filepath)
        self.audio_generator = AudioGenerator(soundfont_filepath)
        self.get_composition_spec()
        self.make_an_echo_chamber()

    def get_composition_spec(self):

        fixed_key_sig = "cmaj"
        chord_vol = 40
        low_vol = 70
        high_vol = 127
        start_chord_pitches = "60,64,67(eb=0)"
        repetition_policy = "tie(pc=70) staccato(pc=10) legato(pc=10) disallow(pc=10)"
        passing_notes_policy = "all(50%) mid(50%)"

        chord_inst = SFHarpsStringsOrchestra.woodwind_Clarinet
        bass_inst1 = SFHarpsStringsOrchestra.woodwind_Bassoon
        bass_inst2 = SFHarpsStringsOrchestra.woodwind_Flute_2
        melody_inst1 = SFHarpsStringsOrchestra.woodwind_Oboe
        melody_inst2 = SFHarpsStringsOrchestra.woodwind_Piccolo

        bar_structure_gen_spec = BarStructureGenSpec(episode_target_duration_ms=60000,
                                                     bar_start_target_duration_ms=5000,
                                                     bar_end_target_duration_ms=4000,
                                                     rhythm="1:1/1:1/1(cb=0,cb=-1,cb=-2) 1:1/1:1/1 1:1/2:1/2,1:2/2:1/2 1:1/4:3/4,1:4/4:1/4")

        chord_sequence_gen_spec = NRTChordSequenceGenSpec(override_chord_pitches="60,64,67(cb=0,cb=-1) none", focal_pitch=63,
                                                          fixed_key_sig=fixed_key_sig, inherit_fixed_key=False,
                                                          start_nro=None, min_cnro_length=1, max_cnro_length=1,
                                                          is_classic=False, majmin_constraint="majmin")

        vl_bass_gen_spec1 = VLMelodyGenSpec(id="contrabass", track_num=0, instrument_num=bass_inst1,
                                            volume=80,
                                            octave_offset=-2,
                                            backbone_length="3 1(cb=-1) 2(cb=-2)",
                                            fixed_key_sig=fixed_key_sig,
                                            note_length=1, passing_notes_policy="all", repetition_policy="disallow")

        vl_bass_gen_spec2 = VLMelodyGenSpec(id="cello", track_num=1, instrument_num=bass_inst2,
                                            volume=f"{low_vol}(ebp=0) {high_vol}(ebp=0.5) {low_vol}(ebp=1)",
                                            octave_offset=-1,
                                            backbone_length="1(cb=-1) 2(cb=-2) 6(pc=33) 7(pc=33) 8(pc=34)",
                                            fixed_key_sig=fixed_key_sig,
                                            note_length=1, passing_notes_policy="mid", repetition_policy="disallow")

        chord_gen_spec_lower = RhythmGenSpec(id="chord_lower", track_num=2, instrument_num=chord_inst,
                                             volume=chord_vol, octave_offset=0,
                                             rhythm="1:1/2:1/2,1:2/2:1/2 1:1/1:1/1(cb=0,cb=-1)", fixed_key_sig=fixed_key_sig)

        chord_gen_spec_mid = RhythmGenSpec(id="chord_mid", track_num=3, instrument_num=chord_inst,
                                           volume=chord_vol, octave_offset=0,
                                           rhythm="2:1/2:1/2,2:2/2:1/2 2:1/1:1/1(cb=0,cb=-1)", fixed_key_sig=fixed_key_sig)

        chord_gen_spec_upper = RhythmGenSpec(id="chord_upper", track_num=4, instrument_num=chord_inst,
                                             volume=chord_vol, octave_offset=0,
                                             rhythm="3:1/2:1/2,3:2/2:1/2 3:1/1:1/1(cb=0,cb=-1)", fixed_key_sig=fixed_key_sig)

        vl_melody_gen_spec1 = VLMelodyGenSpec(id="choir", track_num=5, instrument_num=melody_inst1,
                                              volume=50,
                                              octave_offset=0,
                                              backbone_length="3 1(cb=-1) 2(cb=-2)",
                                              fixed_key_sig=fixed_key_sig,
                                              note_length=1, passing_notes_policy="all", repetition_policy="disallow")

        vl_melody_gen_spec2 = VLMelodyGenSpec(id="flute", track_num=6, instrument_num=melody_inst2,
                                              volume=f"{high_vol}(ebp=0) {low_vol}(ebp=0.5) {high_vol}(ebp=1)",
                                              octave_offset=1,
                                              backbone_length="1(cb=-1) 2(cb=0,cb=-2) 3(pc=20) 4(pc=20) 5(pc=20) 6(pc=20) 7(pc=20)",
                                              fixed_key_sig=fixed_key_sig,
                                              note_length=1, passing_notes_policy="all",
                                              repetition_policy=repetition_policy)

        note_sequence_gen_specs = [vl_bass_gen_spec1, vl_bass_gen_spec2, chord_gen_spec_lower, chord_gen_spec_mid,
                                   chord_gen_spec_upper, vl_melody_gen_spec1, vl_melody_gen_spec2]

        episode1_gen_spec = EpisodeGenSpec(bar_structure_gen_spec,
                                           chord_sequence_gen_spec,
                                           note_sequence_gen_specs)

        episode2_gen_spec = SpecUtils.spec_copy(episode1_gen_spec)
        episode2_gen_spec.bar_structure_gen_spec.bar_start_target_duration_ms = 4000
        episode2_gen_spec.bar_structure_gen_spec.bar_end_target_duration_ms = 5000
        episode2_gen_spec.chord_sequence_gen_spec.fixed_key_sig = None

        episode3_gen_spec = SpecUtils.spec_copy(episode1_gen_spec)

        episode_specs = [episode1_gen_spec, episode2_gen_spec, episode3_gen_spec]
        form_gen_spec = FormGenSpec(episode_specs)
        self.seed = self.fixed_seed if self.fixed_seed is not None else random.randint(0, 100000)
        print("Seed:", self.seed)

        midi_gen_spec = MidiGenSpec(self.soundfont_class_name, self.soundfont_filepath, 3000, True)

        oboe_part_spec = ScorePartGenSpec("Flute", "Flute", [("treble", [6])])
        choir_part_spec = ScorePartGenSpec("Clarinet", "Clarinet", [("treble", [5])])
        strings_part_spec = ScorePartGenSpec("Piano", "Piano", [("treble", [2, 3, 4])])
        cello_part_spec = ScorePartGenSpec("Cello", "Cello", [("bass", [1])])
        bassoon_part_spec = ScorePartGenSpec("Contrabass", "Contrabass", [("bass", [0])])

        part_gen_specs = [oboe_part_spec, choir_part_spec, strings_part_spec, cello_part_spec, bassoon_part_spec]

        score_gen_spec = ScoreGenSpec(part_gen_specs, True, True)
        self.composition_gen_spec = CompositionGenSpec(self.seed, form_gen_spec, score_gen_spec, midi_gen_spec)

    def make_an_echo_chamber(self):
        composition_generator = CompositionGenerator(self.composition_gen_spec)
        os.makedirs(self.output_dir, exist_ok=True)
        self.composition = composition_generator.generate_composition()

    def save_the_echo_chamber(self):
        stem = f"{self.output_dir}/echo_chamber_{self.seed}"
        IOUtils.save_all_aspects(self.composition, self.composition_gen_spec, "Echo Chamber", stem)

    def play_the_echo_chamber(self):
        stem = f"{self.output_dir}/echo_chamber_{self.seed}"
        self.midi_generator.play_composition(f"{stem}.mid", self.composition)

    def edit_the_echo_chamber(self, cmaj_pc, track_num):
        none_pc = 100 - cmaj_pc
        fks = f"cmaj(pc={cmaj_pc}) none(pc={none_pc})"
        editing_spec = InterestingnessEditSpec(track_num=track_num, lower_target_interestingness=1,
                                               upper_target_interestingness=1,
                                               fixed_key_sig=fks,
                                               bar_types_to_change="low_interestingness",
                                               note_types_to_change="all",
                                               pitch_change_choice="closest_to_neighbours",
                                               repetition_policy="disallow(pc=70) allow(pc=10) staccato(pc=10) tie(pc=10)",
                                               chord_notes_fixed=True)

        ListeningUtils.build_interestingness_models()
        listening_model = ListeningUtils.classical_interestingness_model

        for episode in self.composition.form.episodes:
            composition_lead_up_hash = ModelUtils.get_lead_up_notes_hash(self.composition, episode, track_num, 50, True)
            ListeningUtils.annotate(listening_model, composition_lead_up_hash, "fifty", False)
        ListeningUtils.calculate_bar_interestingness_profiles(self.composition, "fifty")

        for episode in self.composition.form.episodes:
            for bar in episode.bars:
                interestingness = bar.interestingness_profile["fifty"]
                bar.score_tag = f"{interestingness:.1f}"

        for ep_num, episode in enumerate(self.composition.form.episodes):
            editor = InterestingnessEditor(editing_spec)
            editing_spec.fixed_key_sig = None if ep_num == 1 else fks
            editor.edit_episode(listening_model, self.composition, episode)

        for episode in self.composition.form.episodes:
            composition_lead_up_hash = ModelUtils.get_lead_up_notes_hash(self.composition, episode, track_num, 50, True)
            ListeningUtils.annotate(listening_model, composition_lead_up_hash, "fifty", False)
        ListeningUtils.calculate_bar_interestingness_profiles(self.composition, "fifty")

        for episode in self.composition.form.episodes:
            for bar in episode.bars:
                interestingness = bar.interestingness_profile["fifty"]
                bar.score_tag = f"{interestingness:.1f} ({bar.score_tag})"

    def handle_discordancy(self):
        edit_spec = DiscordanceEditSpec(interval_scores={1: -2, 11: -1}, score_threshold=-2,
                                        duration_ticks_threshold=400,
                                        ignore_passing_notes=True,
                                        tracks_to_edit=[1, 6], edit_technique="alter")
        editor = DiscordanceEditor(edit_spec, self.composition)
        for episode in self.composition.form.episodes:
            editor.handle_discordances(self.composition, episode)


fixed_seed = None
fixed_seed = 87480
echo_chamber = EchoChamber("SFHarpsStringsOrchestra", SFHarpsStringsOrchestra.soundfont_filepath,
                           "../outputs/echo_chambers", fixed_seed)
echo_chamber.edit_the_echo_chamber(cmaj_pc=100, track_num=6)
echo_chamber.edit_the_echo_chamber(cmaj_pc=100, track_num=1)
#ScoreUtils.wipe_score_colours(echo_chamber.composition)
echo_chamber.handle_discordancy()
echo_chamber.save_the_echo_chamber()
#echo_chamber.play_the_echo_chamber()
