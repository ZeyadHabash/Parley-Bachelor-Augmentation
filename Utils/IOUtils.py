from Parley.Utils.ScoreUtils import *
from Parley.Utils.SpecUtils import *
from Parley.Generators.ScoreGenerator import *
from Parley.Generators.MidiGenerator import *
from Parley.Generators.AudioGenerator import *


class IOUtils:

    def save_all_aspects(composition, composition_gen_spec, save_wav=False):
        stem = composition_gen_spec.output_stem
        soundfont_class = globals()[composition_gen_spec.midi_gen_spec.soundfont_class_name]
        soundfont = soundfont_class()
        soundfont_filepath = soundfont.soundfont_filepath
        midi_generator = MidiGenerator(composition_gen_spec.midi_gen_spec)
        audio_generator = AudioGenerator(soundfont_filepath)
        midi_generator.save_composition(f"{stem}.mid", composition)
        audio_generator.save_mp3(f"{stem}.mp3", f"{stem}.mid")
        if save_wav:
            audio_generator.save_wav(f"{stem}.wav", f"{stem}.mid")
        score_generator = ScoreGenerator(composition_gen_spec.score_gen_spec)
        score_generator.create_score(f"{stem}.musicxml", composition, f"seed: {composition_gen_spec.seed}")
        ScoreUtils.save_pdf(f"{stem}.pdf", f"{stem}.musicxml")
        spec_string = IOUtils.get_composition_gen_spec_string(composition_gen_spec)
        with open(f"{stem}.txt", "w") as f:
            f.write(spec_string)

    def get_composition_gen_spec_string(composition_gen_spec):
        s = IOUtils.get_spec_string(composition_gen_spec.midi_gen_spec)
        for ep_num, episode_gen_spec in enumerate(composition_gen_spec.form_gen_spec.episode_gen_specs):
            s += IOUtils.get_spec_string(episode_gen_spec.bar_structure_gen_spec)
            s += IOUtils.get_spec_string(episode_gen_spec.chord_sequence_gen_spec)
            for note_sequence_gen_spec in episode_gen_spec.note_sequence_gen_specs:
                s += IOUtils.get_spec_string(note_sequence_gen_spec)
        return s

    def get_spec_string(spec):
        s = f"|{type(spec).__name__}|"
        for a in dir(spec):
            if "__" not in a:
                s += f"{a}={getattr(spec, a)}|"
        return s + "\n"

    def read_composition_gen_specs(specs_input_file_path):
        composition_gen_specs = []
        file1 = open(specs_input_file_path, 'r')
        lines = file1.readlines()
        block = []
        blocks = []
        for line in lines:
            if line.strip() == "":
                blocks.append(block)
                block = []
            else:
                block.append(line)
        if len(block) > 1:
            blocks.append(block)
        for block in blocks:
            composition_gen_specs.append(IOUtils.read_composition_gen_spec(block))
        return composition_gen_specs

    def read_composition_gen_spec(block):
        composition_gen_spec = CompositionGenSpec()
        composition_gen_spec.mood_activation_dict = {}
        composition_gen_spec.seeds = []
        composition_gen_spec.form_gen_spec = FormGenSpec()
        episode_gen_spec = EpisodeGenSpec()
        composition_gen_spec.form_gen_spec.episode_gen_specs = [episode_gen_spec]
        episode_gen_spec.note_sequence_gen_specs = []
        for line in block:
            IOUtils.read_composition_gen_spec_line(composition_gen_spec, episode_gen_spec, line)
        return composition_gen_spec

    def read_composition_gen_spec_line(composition_gen_spec, episode_gen_spec, line):
        parts = line.split("|")
        part_id = parts[1]
        if part_id == "CompositionGenSpec":
            lhs = parts[2].split("=")[0]
            rhs = parts[2].split("=")[1]
            if lhs == "seed":
                composition_gen_spec.seed = int(rhs)
        if part_id == "Activations":
            composition_gen_spec.mood_activation_dict = IOUtils.get_mood_activations_dict(parts[1:])
        elif part_id == "MidiGenSpec":
            composition_gen_spec.midi_gen_spec = IOUtils.get_spec_from_parts(part_id, parts[1:])
        elif part_id == "BarStructureGenSpec":
            episode_gen_spec.bar_structure_gen_spec = IOUtils.get_spec_from_parts(part_id, parts[1:])
        elif part_id == "NRTChordSequenceGenSpec":
            episode_gen_spec.chord_sequence_gen_spec = IOUtils.get_spec_from_parts(part_id, parts[1:])
        elif part_id == "RhythmGenSpec" or part_id == "VLMelodyGenSpec":
            episode_gen_spec.note_sequence_gen_specs.append(IOUtils.get_spec_from_parts(part_id, parts[1:]))

    def get_mood_activations_dict(parts):
        dict = {}
        for part in parts:
            if "=" in part:
                lhs = part.split("=")[0]
                rhs = part.split("=")[1]
                dict[lhs] = float(rhs)
        return dict

    def get_spec_from_parts(class_name, parts):
        klass = globals()[class_name]
        spec_class = klass()
        for part in parts:
            if "=" in part:
                param_id = part.split("=")[0]
                param_val = part.split("=")[1]
                if param_val == "None" or param_val == "none":
                    param_val = None
                elif param_val == "True":
                    setattr(spec_class, param_id, True)
                elif param_val == "False":
                    setattr(spec_class, param_id, False)
                else:
                    try:
                        param_val = int(param_val)
                    except:
                        try: param_val = float(param_val)
                        except:
                            pass
                setattr(spec_class, param_id, param_val)
        return spec_class