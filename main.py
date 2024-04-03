"""
inst_types = ["piano", "epiano", "keyboard", "woodwind", "brass", "synth", "guitar", "strings", "voice", "orchestra"]
midi_gen_spec = MidiGenSpec("SFFluidSynth", SFFluidSynth.soundfont_filepath, True, True)
excerpt_gen_spec = ExcerptGenSpec(inst_types, inst_types, midi_gen_spec)
generator = ExcerptGenerator(excerpt_gen_spec)
composition_gen_spec = generator.get_excerpt_gen_spec(include_percussion=True)
generator.save_excerpts("../outputs/excerpts/", composition_gen_spec, 1)
"""

"""
from sf2utils.sf2parse import Sf2File
with open('../soundfonts/FluidR3_GM.sf2', 'rb') as sf2_file:
    sf2 = Sf2File(sf2_file)
    for p in sf2.presets:
        try:
            if p.bank == 0:
                print(p.name, p.preset, p.bank)
        except:
            pass

    print(sf2.samples[91].name)
    print(sf2.instruments[17].bags[0].pretty_print())

    #note_ids = []
    #for sample in sf2.samples:
    #    print(sample.name, sample.original_pitch, sample.sample_link, sample.pitch_correction)
    #print(dir(sf2.samples[117]))


def get_best_for_tag(tag):
    triples = []
    for composition_gen_spec in composition_gen_specs:
        for ind, mood_dict in enumerate(composition_gen_spec.mood_activation_dicts):
            triples.append((composition_gen_spec, mood_dict, composition_gen_spec.seeds[ind]))
    triples.sort(key=lambda x: x[1][tag])
    best_triple = triples[-1]
    print(best_triple[1][tag])
    best_composition_gen_spec = best_triple[0]
    best_composition_gen_spec.seed = best_triple[2]
    reconstruct_composition(best_composition_gen_spec, tag)

def reconstruct_composition(composition_gen_spec, stem):
    melody_inst_num = composition_gen_spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs[3].instrument_num
    chord_inst_num = composition_gen_spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs[0].instrument_num
    soundfont_class_name = composition_gen_spec.midi_gen_spec.soundfont_class_name
    melody_inst, _ = SoundfontUtils.get_instrument_name_and_type(soundfont_class_name, melody_inst_num)
    chord_inst, _ = SoundfontUtils.get_instrument_name_and_type(soundfont_class_name, chord_inst_num)
    part1 = ScorePartGenSpec("Melody", melody_inst, [("treble", [3])])
    part2 = ScorePartGenSpec("Chords", chord_inst, [("bass", [0, 1, 2])])
    part_gen_specs = [part1, part2]
    composition_gen_spec.score_gen_spec = ScoreGenSpec(part_gen_specs, True, True)
    generator = CompositionGenerator(composition_gen_spec)
    return generator.generate_composition()

composition_gen_specs = IOUtils.read_composition_gen_specs("./mmm.txt")

for spec in composition_gen_specs:
    stem = f"./outputs/showcase/showcase_mmm_{spec.seed}"
    composition = reconstruct_composition(spec, stem)
    IOUtils.save_all_aspects(composition, spec, "Excerpt", stem)

composition_duration_ms = (1000 * 60 * 6) - 3100
num_cycles = 2
fixed_seed = None
#fixed_seed = 9215

flaneur = make_a_flaneur("Flaneur", fixed_seed, output_dir="./Outputs/Flaneurs",
                         composition_duration_ms=composition_duration_ms, num_cycles=num_cycles,
                         edit_the_flaneur=False, random_edit_the_flaneur=False,
                         add_first_harmony=True, add_second_harmony=False,
                         num_highlight_passages=5)

from Parley.CompositionSpecs.Flaneur import *
do_flaneur_experiments()

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdfminer.converter import 

output_string = StringIO()
with open(c, 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

print(output_string.getvalue())

for page_layout in extract_pages("./Outputs/Excerpts/excerpt_173483.pdf"):
    for element in page_layout:
        if isinstance(element, LTCurve) or isinstance(element, LTLine):
            print(element.bbox)
"""

"""
from Parley.Generators.ExcerptGenerator import *

def get_excerpt(include_percussion):
    inst_types = ["piano", "epiano", "keyboard", "woodwind", "brass", "synth", "guitar", "strings", "voice", "orchestra"]
    midi_gen_spec = MidiGenSpec("SFFluidSynth", SFFluidSynth.soundfont_filepath, None)
    excerpt_gen_spec = ExcerptGenSpec(inst_types, inst_types, midi_gen_spec)

    generator = ExcerptGenerator(excerpt_gen_spec)
    seed = random.randint(0, 1000000)

    output_stem = f"./Outputs/Excerpts/excerpt_{seed}"
    composition_gen_spec = generator.get_excerpt_gen_spec(output_stem, include_percussion)
    composition_gen_spec.mood_activations_dicts = []
    composition_gen_spec.seed = seed
    composition_generator = CompositionGenerator(composition_gen_spec)
    composition = composition_generator.generate_entire_composition()
    IOUtils.save_all_aspects(composition, composition_gen_spec, False)

for i in range(0, 10):
    get_excerpt(True)

"""

from Parley.Utils.PDFUtils import *

from pdf2image import convert_from_path
from PIL import ImageDraw, Image
from Parley.Generators.VideoGenerator import *

from Parley.CompositionSpecs.Flaneur import *


num_minutes = 6
composition_duration_ms = (1000 * 60 * num_minutes) - 3100
num_cycles = 2
fixed_seed = None
fixed_seed = 16057

flaneur = make_a_flaneur("Flaneur", fixed_seed, output_dir="./Outputs/Flaneurs",
                         composition_duration_ms=composition_duration_ms, num_cycles=num_cycles,
                         edit_the_flaneur=True, random_edit_the_flaneur=False,
                         add_first_harmony=True, add_second_harmony=False,
                         num_highlight_passages=5, make_video=True)

"""
from Parley.Utils.DebugUtils import *

DebugUtils.debug_pdf_annotations("./Outputs/Flaneurs/flaneur_29052.pdf")
"""
