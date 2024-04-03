from Parley.Specifications.GeneratorStructure import *
from Parley.Utils.IOUtils import *
from Parley.Editors.InterestingnessEditor import *
from Parley.Editors.HarmonisationEditor import *
from Parley.Editors.RandomEditor import *
from Parley.Editors.DiscordanceEditor import *
from Parley.Utils.AnalysisUtils import *
from Parley.Utils.DataUtils import *
from Parley.Analysers.InterestingnessEditAnalyser import *
from Parley.Utils.AnnotationUtils import *
#from Parley.Generators.VideoGenerator import *
from Parley.Editors.SimplifyingTiedNoteEditor import *
from Parley.Editors.RepeatedNoteRemovalEditor import *
from Parley.Editors.RhythmRepetitionEditor import *


class Flaneur:

    def __init__(self, title, soundfont_class_name, soundfont_filepath, instrument_num, output_dir, fixed_seed=None,
                 composition_duration_ms=100000, num_cycles=10, rh_has_triples=False,
                 ep1_passing_notes_policy="all", ep2_passing_notes_policy="all",
                 repetition_policy="allow", num_highlight_passages=3):
        self.title = title
        self.soundfont_class_name = soundfont_class_name
        self.soundfont_filepath = soundfont_filepath
        self.instrument_num = instrument_num
        self.output_dir = output_dir
        self.fixed_seed = fixed_seed
        self.rh_has_triples = rh_has_triples
        self.ep1_passing_notes_policy = ep1_passing_notes_policy
        self.ep2_passing_notes_policy = ep2_passing_notes_policy
        self.repetition_policy = repetition_policy
        self.num_highlight_passages = num_highlight_passages
        self.composition_gen_spec = None
        self.seed = None
        self.composition = None
        self.lead_sheet = None
        self.get_composition_spec(composition_duration_ms, num_cycles)
        composition_generator = CompositionGenerator(self.composition_gen_spec)
        self.lead_sheet, self.lead_sheet_cgs = composition_generator.generate_composition_lead_sheet()
        self.composition = composition_generator.generate_entire_composition()

    def get_composition_spec(self, composition_duration_ms, num_cycles):

        num_episodes = 2 + (num_cycles * 3)
        episode_duration = composition_duration_ms//num_episodes

        fixed_key_sig = "cmaj"
        chord_volume_a = "60(ebp=0) 100(ebp=1)"
        chord_volume_b = "100(ebp=0) 60(ebp=1)"
        melody_volume_a = "80(ebp=0) 120(ebp=1)"
        melody_volume_b = "120(ebp=0) 80(ebp=1)"

        bar_structure_gen_spec = BarStructureGenSpec(episode_target_duration_ms=episode_duration,
                                                     bar_start_target_duration_ms=3000, # 2000
                                                     bar_end_target_duration_ms=2500, # 1800
                                                     rhythm="1:1/1:1/1(ebc=0,eb=-1) 1:1/2:1/2,1:2/2:1/2(ebc=1,ebc=2) 1:1/4:3/4,1:4/4:1/4(ebc=3)")

        chord_sequence_gen_spec = NRTChordSequenceGenSpec(override_chord_pitches="69,72,76(cb=0,cb=-1)", focal_pitch=70,
                                                          fixed_key_sig=fixed_key_sig, max_repetitions=1,
                                                          start_nro=None, min_cnro_length=5, max_cnro_length=10,
                                                          is_classic=False, majmin_constraint="min")

        bass_gen_spec = RhythmGenSpec(id="bass", track_num=0, channel_num=0, instrument_num=self.instrument_num,
                                      volume=chord_volume_a, leads_dynamics_direction=False, octave_offset=-2,
                                      rhythm="1:1/8:2/8,1:5/8:2/8(cbc=0,cbc=1,cbc=2) 1:1/8:2/8(cbc=3) 1:1/8:2/8,1:5/8:4/8(cb=-1)",
                                      fixed_key_sig=fixed_key_sig)

        chord_gen_spec_lower = RhythmGenSpec(id="chord_lower", track_num=1, channel_num=1, instrument_num=self.instrument_num,
                                             volume=chord_volume_a, leads_dynamics_direction=False, octave_offset=-1,
                                             rhythm="1:3/8:2/8,1:7/8:2/8(cbc=0,cbc=1,cbc=2) 1:3/8:2/8,1:5/8:2/8,1:7/8:2/8(cbc=3) 1:3/8:2/8(cb=-1)",
                                             fixed_key_sig=fixed_key_sig)

        chord_gen_spec_mid = RhythmGenSpec(id="chord_mid", track_num=2, channel_num=2, instrument_num=self.instrument_num,
                                           volume=chord_volume_a, leads_dynamics_direction=False, octave_offset=-1,
                                           rhythm="2:3/8:2/8,2:7/8:2/8(cbc=0,cbc=1,cbc=2) 2:3/8:2/8,2:5/8:2/8,2:7/8:2/8(cbc=3) 2:3/8:2/8(cb=-1)",
                                           fixed_key_sig=fixed_key_sig)

        chord_gen_spec_upper = RhythmGenSpec(id="chord_upper", track_num=3, channel_num=3, instrument_num=self.instrument_num,
                                             volume=chord_volume_a, leads_dynamics_direction=False, octave_offset=-1,
                                             rhythm="3:3/8:2/8,3:7/8:2/8(cbc=0,cbc=1,cbc=2) 3:3/8:2/8,3:5/8:2/8,3:7/8:2/8(cbc=3) 3:3/8:2/8(cb=-1)",
                                             fixed_key_sig=fixed_key_sig)

        vl_melody_gen_spec = VLMelodyGenSpec(id="melody", track_num=4, channel_num=4, instrument_num=self.instrument_num,
                                             volume=melody_volume_a, leads_dynamics_direction=True, octave_offset=0,
                                             backbone_length="1(cb=0,cb=-1) 3(pc=50) 4(pc=50)",
                                             fixed_key_sig=fixed_key_sig,
                                             note_length=1, passing_notes_policy=self.ep1_passing_notes_policy,
                                             repetition_policy=self.repetition_policy)

        note_sequence_gen_specs = [bass_gen_spec, chord_gen_spec_lower, chord_gen_spec_mid,
                                   chord_gen_spec_upper, vl_melody_gen_spec]

        episode1_gen_spec = EpisodeGenSpec(bar_structure_gen_spec, chord_sequence_gen_spec, note_sequence_gen_specs)

        episode2_gen_spec = SpecUtils.spec_copy(episode1_gen_spec)
        episode2_gen_spec.chord_sequence_gen_spec.override_chord_pitches = "64,67,72(eb=0,eb=-1)"
        ep2_bar_spec = episode2_gen_spec.bar_structure_gen_spec
        ep2_bar_spec.bar_start_target_duration_ms = 2500 #1800
        ep2_bar_spec.bar_end_target_duration_ms = 3000 #2000
        episode2_gen_spec.chord_sequence_gen_spec.majmin_constraint = "maj"
        ep2_melody_spec = episode2_gen_spec.note_sequence_gen_specs[-1]
        ep2_melody_spec.passing_notes_policy = self.ep2_passing_notes_policy
        ep2_melody_spec.backbone_length = "6(pc=20) 7(pc=50) 8(pc=30)"
        ep2_melody_spec.volume = melody_volume_b
        for track_num in range(0, 3):
            episode2_gen_spec.note_sequence_gen_specs[track_num].volume = chord_volume_b

        episode_specs = [episode1_gen_spec, episode2_gen_spec]
        for cycles in range(0, num_cycles):
            episode3_gen_spec = SpecUtils.spec_copy(episode1_gen_spec)
            episode4_gen_spec = SpecUtils.spec_copy(episode2_gen_spec)
            episode5_gen_spec = SpecUtils.spec_copy(episode1_gen_spec)
            episode5_gen_spec.note_sequence_gen_specs[4].backbone_length = "3(ebp=0) 2(ebp=1) 1(cb=-1)"
            episode_specs.extend([episode3_gen_spec, episode4_gen_spec, episode5_gen_spec])

        form_gen_spec = FormGenSpec(episode_specs)
        self.seed = self.fixed_seed if self.fixed_seed is not None else random.randint(0, 100000)
        print("Seed:", self.seed)

        midi_gen_spec = MidiGenSpec(self.soundfont_class_name, self.soundfont_filepath, 3000)
        part_gen_specs = [ScorePartGenSpec("Piano", "Piano", [("treble", [4, 5]), ("bass", [0, 1, 2, 3])])]
        if self.rh_has_triples:
           part_gen_specs = [ScorePartGenSpec("Piano", "Piano", [("treble", [4, 5, 6]), ("bass", [0, 1, 2, 3])])]
        score_gen_spec = ScoreGenSpec("Flaneur", part_gen_specs, True, True, False)
        lead_sheet_gen_spec = LeadSheetGenSpec()
        output_stem = self.output_dir + f"/flaneur_{self.seed}"
        self.composition_gen_spec = CompositionGenSpec(self.title, self.seed, output_stem, form_gen_spec,
                                                       lead_sheet_gen_spec, score_gen_spec, midi_gen_spec)

    def add_melody_harmony(self, track_num_to_harmonise):

        editing_spec = HarmonisationEditSpec(id="harmony", new_track_num=track_num_to_harmonise + 1,
                                             new_channel_num=track_num_to_harmonise + 1,
                                             instrument_num=self.instrument_num,
                                             track_num_to_harmonise=track_num_to_harmonise,
                                             fixed_key_sig="cmaj",
                                             note_types_to_change="passing",
                                             intervals_allowed=[-3, -5, -8, 4, 7, 9],
                                             pitch_range_low=60, pitch_range_high=72,
                                             map_to_key_signature=False)

        for ind, episode in enumerate(self.composition.form.episodes):
            spec = SpecUtils.spec_copy(editing_spec)
            if ind == 1:
                spec.pitch_range_low = 72
                spec.pitch_range_high = 100
            harmony_editor = HarmonisationEditor(spec)
            harmony_editor.add_harmony_track(self.composition, episode)
        harmony_editor = HarmonisationEditor(editing_spec)
        harmony_editor.handle_tied_notes(self.composition)

    def score_the_flaneur(self):

        """
        for episode in self.composition.form.episodes:
            composition_lead_up_hash = ModelUtils.get_lead_up_notes_hash(self.composition, episode, 4, 50, True)
            ListeningUtils.annotate(listening_model, composition_lead_up_hash, "fifty", False)
        ListeningUtils.calculate_bar_interestingness_profiles(self.composition, "fifty")

        for episode in self.composition.form.episodes:
            for bar in episode.bars:
                interestingness = bar.interestingness_profile["fifty"]
                bar.score_tag = f"{interestingness:.1f}"
        """


    def edit_the_flaneur(self, cmaj_pc, redo_scores=True, repetition_policy="allow", fix_chord_notes=True):
        none_pc = 100 - cmaj_pc
        fks = f"cmaj(pc={cmaj_pc}) none(pc={none_pc})"
        editing_spec = InterestingnessEditSpec(track_num=0, lower_target_interestingness=1,
                                               upper_target_interestingness=1,
                                               fixed_key_sig=fks,
                                               bar_types_to_change="all",
                                               note_types_to_change="all",
                                               pitch_change_choice="closest_to_neighbours",
                                               focal_pitch=None,
                                               repetition_policy=repetition_policy,
                                               chord_notes_fixed=fix_chord_notes)

        ListeningUtils.build_interestingness_models()
        listening_model = ListeningUtils.classical_interestingness_model

        # self.score_the_flaneur()

        for track_num in range(0, 5):
            editing_spec.track_num = track_num
            for episode in self.composition.form.episodes:
                editing_spec.repetition_policy = "allow" if track_num < 4 else repetition_policy
                if track_num == 4:
                    editing_spec.repetition_policy = repetition_policy
                    editing_spec.pitch_change_choice = "closest_to_neighbours"
                elif track_num == 0:
                    editing_spec.repetition_policy = "allow"
                    editing_spec.pitch_change_choice = "closest_to_neighbours"
                    editing_spec.focal_pitch = None
                else:
                    editing_spec.repetition_policy = "allow"
                    editing_spec.pitch_change_choice = "focal_pitch"
                    editing_spec.focal_pitch = 55
                editor = InterestingnessEditor(editing_spec)
                editor.edit_episode(listening_model, self.composition, episode)

        removal_spec = RepeatedNoteRemovalEditSpec(ordered_track_nums=[1, 2, 3, 0, 4])
        repeated_note_removal_editor = RepeatedNoteRemovalEditor(removal_spec)
        repeated_note_removal_editor.remove_repeated_notes(self.composition)

        simplifier = SimplifyingTiedNoteEditor(None)
        simplifier.simplify_track(self.composition, 4)

        rhythm_edit_spec = RhythmRepetitionEditSpec(rhythm_track_num=4, max_num_repetitions=20,
                                                    min_num_notes_in_rhythm=6, num_bars_in_window=10)
        editor = RhythmRepetitionEditor(rhythm_edit_spec)
        editor.copy_rhythms(self.composition)

        """
        if redo_scores:
            self.score_the_flaneur()
        """

    def random_edit_the_flaneur(self, cmaj_pc):
        fks = f"cmaj(pc={cmaj_pc}) none(pc={100 - cmaj_pc})"
        spec = RandomEditSpec(track_num=4, change_prop=False, fixed_key_sig=fks)
        random_editor = RandomEditor(spec)
        for episode in self.composition.form.episodes:
            random_editor.edit_episode(self.composition, episode)

    def handle_discordancy(self):
        edit_spec = DiscordanceEditSpec(interval_scores={1: -2, 11: -1}, score_threshold=-2,
                                        duration_ticks_threshold=400, ignore_passing_notes=True,
                                        tracks_to_edit=[4, 5], edit_technique="alter")
        editor = DiscordanceEditor(edit_spec, self.composition)
        for episode in self.composition.form.episodes:
            editor.handle_discordances(self.composition, episode)

    def save_the_flaneur(self, save_wav):
        IOUtils.save_all_aspects(self.lead_sheet, self.lead_sheet_cgs, save_wav)
        IOUtils.save_all_aspects(self.composition, self.composition_gen_spec, save_wav)

    def play_the_flaneur(self):
        stem = f"{self.output_dir}/flaneur_{self.seed}"
        self.midi_generator.play_composition(f"{stem}.mid", self.composition, True)

    def analyse_the_flaneur(self):
        spec = InterestingnessEditAnalyserSpec(track_num=4, min_num_notes=4,
                                               num_highlight_passages=self.num_highlight_passages,
                                               make_notes_purple=True)
        analyser = InterestingnessEditAnalyser(spec)
        analyser.analyseComposition(self.composition)

    """
    def make_flaneur_video(self):
        vgen_spec = VideoGenSpec(dpi=100, fps=16, line_start_bar_indent_pc=10)
        video_generator = VideoGenerator(vgen_spec)
        video_generator.make_performance_video(self.composition_gen_spec, self.composition)
    """


def do_flaneur_experiments():
    num_trials = 100
    all_analyses_dict = {}
    for trial_num in range(0, num_trials):
        print("*****************", trial_num, "*****************")
        fixed_seed = random.randint(0, 1000000)
        analysis_dict = do_flaneur_trial(trial_num, fixed_seed)
        for key in analysis_dict:
            analysis_list = [] if key not in all_analyses_dict else all_analyses_dict[key]
            analysis_list.append(analysis_dict[key])
            all_analyses_dict[key] = analysis_list
    for key in all_analyses_dict:
        print(key)
        av_analysis = DataUtils.get_average_dataobject(all_analyses_dict[key])
        print(DataUtils.dataobject_string(av_analysis))


def do_flaneur_trial(trial_num, fixed_seed):
    composition_duration_ms = 120000
    num_cycles = 1
    analysis_dict = {}
    for passing_notes_policy in ["all", "none", "mid", "all(pc=33) mid(pc=33) none(pc=34)"]:
        flaneurs = []
        for flaneur_num in range(0, 4):

            flaneur = Flaneur("Flaneur", "SFYamahaPiano", SFYamahaPiano.soundfont_filepath,
                              SFYamahaPiano.piano_YamahaS6, "./Outputs/Flaneurs", fixed_seed,
                              composition_duration_ms, num_cycles, False, passing_notes_policy,
                              passing_notes_policy, repetition_policy="allow", num_highlight_passages=3)

            if flaneur_num == 1:
                flaneur.edit_the_flaneur(cmaj_pc=100, redo_scores=False, repetition_policy="allow", fix_chord_notes=True)
            if flaneur_num == 2:
                flaneur.edit_the_flaneur(cmaj_pc=100, redo_scores=False, repetition_policy="allow", fix_chord_notes=False)
            if flaneur_num == 3:
                flaneur.random_edit_the_flaneur(cmaj_pc=100)
            flaneurs.append(flaneur)

        analysis_dict[(passing_notes_policy, "voice leading")] = AnalysisUtils.get_musical_analysis(flaneurs[0].composition, 4)
        analysis_dict[(passing_notes_policy, "interestingness_mapped")] = AnalysisUtils.get_musical_analysis(flaneurs[1].composition, 4)
        analysis_dict[(passing_notes_policy, "interestingness_not_mapped")] = AnalysisUtils.get_musical_analysis(flaneurs[2].composition, 4)
        analysis_dict[(passing_notes_policy, "random")] = AnalysisUtils.get_musical_analysis(flaneurs[3].composition, 4)

    return analysis_dict


def make_a_flaneur(title, fixed_seed, output_dir="./Outputs/Flaneurs", composition_duration_ms=300000, num_cycles=3,
                   edit_the_flaneur=False, random_edit_the_flaneur=False,
                   add_first_harmony=False, add_second_harmony=False,
                   ep1_passing_notes_policy="all(pc=60) mid(pc=30) none(pc=10)",
                   ep2_passing_notes_policy="mid(pc=50) none(pc=50)",
                   repetition_policy="tie(pc=60) staccato(pc=20) legato(pc=10) disallow(pc=10)",
                   num_highlight_passages=5, fix_edit_chord_notes=True,
                   make_video=False):

    flaneur = Flaneur(title, "SFYamahaPiano", SFYamahaPiano.soundfont_filepath,
                      SFYamahaPiano.piano_YamahaS6, output_dir, fixed_seed,
                      composition_duration_ms, num_cycles, add_second_harmony,
                      ep1_passing_notes_policy, ep2_passing_notes_policy,
                      repetition_policy, num_highlight_passages)

    if random_edit_the_flaneur:
        flaneur.random_edit_the_flaneur(cmaj_pc=100)
    if edit_the_flaneur:
        flaneur.edit_the_flaneur(cmaj_pc=100, repetition_policy=repetition_policy, fix_chord_notes=fix_edit_chord_notes)
    if add_first_harmony:
        flaneur.add_melody_harmony(track_num_to_harmonise=4)
    if add_second_harmony:
        flaneur.add_melody_harmony(track_num_to_harmonise=5)

    #ScoreUtils.wipe_score_colours(flaneur.composition)
    #flaneur.handle_discordancy()
    #flaneur.play_the_flaneur()
    #analysis = AnalysisUtils.get_musical_analysis(flaneur.composition, 4)
    #print(DataUtils.dataobject_string(analysis))

    flaneur.analyse_the_flaneur()
    #bar_and_counts = AnnotationUtils.annotate_backbone_notes(flaneur.composition, 4)
    #print(bar_and_counts)

    flaneur.save_the_flaneur(save_wav=True)

    #if make_video:
    #    flaneur.make_flaneur_video()

    return flaneur

"""

images = convert_from_path("./Outputs/Flaneurs/flaneur_434.pdf", dpi=300)

bar_boxes = PDFUtils.get_bar_bounding_boxes("./Outputs/Flaneurs/flaneur_434.pdf", 2)

image = Image.new('RGBA', images[0].size)
image.paste(images[0])
context = ImageDraw.Draw(image)

for ind, bar_line in enumerate(bar_lines):
    if bar_line.page_num == 0:
        box = bar_line.scale_to_image(images[0])
        shape = ((box.x1, box.y1), (box.x2, box.y2))
        colour = ["red", "green", "blue"][ind % 3]
        context.rectangle(shape, fill=(100, 0, 0, 255), outline=colour, width=5)

image.show()

"""
