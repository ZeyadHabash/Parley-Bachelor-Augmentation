from Parley.Generators.StandardBarStructureGenerator import *
from Parley.Generators.NRTChordSequenceGenerator import *
from Parley.Generators.RhythmNoteSequenceGenerator import *
from Parley.Generators.VLMelodyGenerator import *
from Parley.Specifications.Specifications import *
from Parley.Generators.LeadSheetGenerator import *


class CompositionGenerator:

    def __init__(self, composition_gen_spec):
        self.composition_gen_spec = composition_gen_spec

    def generate_composition_form(self):
        random.seed(self.composition_gen_spec.seed)
        form_generator = FormGenerator(self.composition_gen_spec,
                                       self.composition_gen_spec.form_gen_spec)
        return form_generator.generate_form()

    def generate_composition_lead_sheet(self):
        form = self.generate_composition_form()
        lead_sheet_generator = LeadSheetGenerator(self.composition_gen_spec.lead_sheet_gen_spec)
        return lead_sheet_generator.generate_lead_sheet(form, self.composition_gen_spec)

    def generate_entire_composition(self):
        form = self.generate_composition_form()
        num_episodes = len(self.composition_gen_spec.form_gen_spec.episode_gen_specs)
        episode_generators = []
        for episode_spec in self.composition_gen_spec.form_gen_spec.episode_gen_specs:
            episode_generators.append(EpisodeGenerator(episode_spec))
        for pass_num in range(0, 3):
            for i, episode_generator in enumerate(episode_generators):
                previous_episode = None if i == 0 else form.episodes[i-1]
                next_episode = None if (i == num_episodes - 1) else form.episodes[i+1]
                episode_generator.calculate_note_sequences(pass_num, previous_episode, form.episodes[i], next_episode)
        composition = Composition(self.composition_gen_spec.title, form)
        return composition


class FormGenerator:

    def __init__(self, composition_gen_spec, form_gen_spec):
        self.composition_gen_spec = composition_gen_spec
        self.form_gen_spec = form_gen_spec

    def generate_form(self):
        num_episodes = len(self.form_gen_spec.episode_gen_specs)
        episodes = [Episode(title=f"Episode {i+1}", bars=None, interestingness_profile=None, score_notes=[]) for i in range(0, num_episodes)]
        episode_generators = []
        for episode_spec in self.form_gen_spec.episode_gen_specs:
            episode_generators.append(EpisodeGenerator(episode_spec))
        for i, episode_generator in enumerate(episode_generators):
            previous_episode = None if i == 0 else episodes[i - 1]
            episode_generator.calculate_empty_bars(previous_episode, episodes[i])
        num_bars = sum([len(x.bars) for x in episodes])
        for episode in episodes:
            for bar in episode.bars:
                bar.num_bars_to_comp_end = num_bars - bar.comp_bar_num - 1
                bar.num_bars_to_ep_end = len(episode.bars) - bar.ep_bar_num - 1
        for i, episode_generator in enumerate(episode_generators):
            previous_episode = None if i == 0 else episodes[i - 1]
            episode_generator.add_chord_positions(previous_episode, episodes[i])
        for i, episode_generator in enumerate(episode_generators):
            previous_episode = None if i == 0 else episodes[i - 1]
            next_episode = None if (i == num_episodes - 1) else episodes[i + 1]
            episode_generator.calculate_chord_sequence(previous_episode, episodes[i], next_episode)
        return Form(episodes)


class EpisodeGenerator:

    def __init__(self, episode_gen_spec):
        self.episode_gen_spec = episode_gen_spec
        self.note_sequence_generators = []
        for note_sequence_gen_spec in self.episode_gen_spec.note_sequence_gen_specs:
            if isinstance(note_sequence_gen_spec, RhythmGenSpec):
                note_sequence_generator = RhythmNoteSequenceGenerator(note_sequence_gen_spec)
                self.note_sequence_generators.append(note_sequence_generator)
            elif isinstance(note_sequence_gen_spec, VLMelodyGenSpec):
                note_sequence_generator = VLMelodyGenerator(note_sequence_gen_spec)
                self.note_sequence_generators.append(note_sequence_generator)

    def calculate_empty_bars(self, previous_episode, this_episode):
        bar_structure_generator = BarStructureGenerator(self.episode_gen_spec.bar_structure_gen_spec)
        bar_structure_generator.calculate_empty_bars(previous_episode, this_episode)

    def add_chord_positions(self, previous_episode, this_episode):
        bar_structure_generator = BarStructureGenerator(self.episode_gen_spec.bar_structure_gen_spec)
        bar_structure_generator.add_chord_positions(previous_episode, this_episode)

    def calculate_chord_sequence(self, previous_episode, this_episode, next_episode):
        chord_sequence_generator = ChordSequenceGenerator(self.episode_gen_spec.chord_sequence_gen_spec)
        chord_sequence_generator.update_chords(previous_episode, this_episode, next_episode)

    def calculate_note_sequences(self, pass_num, previous_episode, this_episode, next_episode):
        for note_sequence_generator in self.note_sequence_generators:
            note_sequence_generator.update_note_sequence(pass_num, previous_episode, this_episode, next_episode)


class BarStructureGenerator:

    def __init__(self, bar_structure_gen_spec):
        self.bar_structure_gen_spec = bar_structure_gen_spec

    def calculate_empty_bars(self, previous_episode, this_episode):
        generator = StandardBarStructureGenerator(self.bar_structure_gen_spec)
        generator.calculate_empty_bars(previous_episode, this_episode)

    def add_chord_positions(self, previous_episode, this_episode):
        generator = StandardBarStructureGenerator(self.bar_structure_gen_spec)
        generator.add_chord_positions(previous_episode, this_episode)


class ChordSequenceGenerator:

    def __init__(self, chord_sequence_gen_spec):
        self.chord_sequence_gen_spec = chord_sequence_gen_spec

    def update_chords(self, previous_episode, this_episode, next_episode):
        if isinstance(self.chord_sequence_gen_spec, NRTChordSequenceGenSpec):
            chord_sequence_generator = NRTChordSequenceGenerator(self.chord_sequence_gen_spec)
            chord_sequence_generator.update_chords(previous_episode, this_episode, next_episode)