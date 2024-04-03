from Parley.Utils.IOUtils import *
from Parley.GeneratorStructure import *
from Parley.Designers.ExcerptExpanderDesigner import *
from Parley.Utils.ListeningUtils import *
from Parley.Utils.ModelUtils import *
from Parley.Editors.InterestingnessEditor import *


class MMM:

    def __init__(self, excerpt_design_spec, excerpt_gen_spec):
        self.excerpt_design_spec = excerpt_design_spec
        self.excerpt_gen_spec = excerpt_gen_spec
        designer = ExcerptExpanderDesigner(excerpt_design_spec)
        self.composition_gen_spec = designer.design_composition_spec(excerpt_gen_spec)
        generator = CompositionGenerator(self.composition_gen_spec)
        self.composition = generator.generate_composition()

    def edit_composition(self):
        editing_spec = InterestingnessEditSpec(track_num=3, lower_target_interestingness=1,
                                               upper_target_interestingness=1,
                                               fixed_key_sig=None,
                                               bar_types_to_change="low_interestingness",
                                               note_types_to_change="all",
                                               pitch_change_choice="closest_to_neighbours",
                                               repetition_policy="disallow(pc=70) allow(pc=10) staccato(pc=10) tie(pc=10)",
                                               chord_notes_fixed=True)

        ListeningUtils.build_interestingness_models()
        listening_model = ListeningUtils.classical_interestingness_model

        for episode in self.composition.form.episodes:
            composition_lead_up_hash = ModelUtils.get_lead_up_notes_hash(self.composition, episode, 3, 50, True)
            ListeningUtils.annotate(listening_model, composition_lead_up_hash, "fifty", False)
        ListeningUtils.calculate_bar_interestingness_profiles(self.composition, "fifty")

        for episode in self.composition.form.episodes:
            for bar in episode.bars:
                interestingness = bar.interestingness_profile["fifty"]
                bar.score_tag = f"{interestingness:.1f}"

        for episode in self.composition.form.episodes:
            editor = InterestingnessEditor(editing_spec)
            editor.edit_episode(listening_model, self.composition, episode)

        for episode in self.composition.form.episodes:
            composition_lead_up_hash = ModelUtils.get_lead_up_notes_hash(self.composition, episode, 3, 50, True)
            ListeningUtils.annotate(listening_model, composition_lead_up_hash, "fifty", False)
        ListeningUtils.calculate_bar_interestingness_profiles(self.composition, "fifty")

        for episode in self.composition.form.episodes:
            for bar in episode.bars:
                interestingness = bar.interestingness_profile["fifty"]
                bar.score_tag = f"{interestingness:.1f} ({bar.score_tag})"


excerpt_gen_specs = IOUtils.read_composition_gen_specs("../mmm.txt")
design_spec = ExcerptExpanderDesignSpec(composition_duration_ms=240000,
                                        num_episodes=8,
                                        volume_cycle="0,10,0,-10",
                                        tempo_cycle="0,10,0,-10")

for s in excerpt_gen_specs:
    mmm = MMM(design_spec, s)
    mmm.edit_composition()
    stem = f"../outputs/showcase/showcase_mmm_{mmm.composition_gen_spec.seed}"
    IOUtils.save_all_aspects(mmm.composition, mmm.composition_gen_spec, "Melancholic, Meditative and Motivational", stem)

