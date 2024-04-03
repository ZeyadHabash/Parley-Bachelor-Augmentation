from Parley.Utils.IOUtils import *
from Parley.GeneratorStructure import *
from Parley.Utils.SoundfontUtils import *

def get_notable_tags(activations_dict):
  s = ""
  count = 0
  for tag in activations_dict.keys():
    activation = activations_dict[tag]
    if activation > (mean_dict[tag] + (2 * std_dict[tag])):
      s += tag + " "
      count += 1
      if count % 10 == 0:
        s += "\n"
  return s


composition_gen_specs = IOUtils.read_composition_gen_specs("../excerpts.txt")
with_percussion_specs = []
without_percussion_specs = []

for spec in composition_gen_specs:
  if len(spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs) == 4:
    without_percussion_specs.append(spec)
  else:
    with_percussion_specs.append(spec)

activations_dict = {}
mean_dict = {}
std_dict = {}

for s in composition_gen_specs:
  for mood in s.mood_activation_dict:
    if mood not in activations_dict:
      activations_dict[mood] = []
    activations_dict[mood].append(s.mood_activation_dict[mood])

for mood in activations_dict:
  mean_dict[mood] = np.mean(activations_dict[mood])
  std_dict[mood] = np.std(activations_dict[mood])

tags = ["action", "adventure", "advertising", "background", "ballad", "calm", "children", "christmas", "commercial", "cool", "corporate", "dark", "deep", "documentary", "drama", "dramatic", "dream", "emotional", "energetic", "epic", "fast", "film", "fun", "funny", "game", "groovy", "happy", "heavy", "holiday", "hopeful", "inspiring", "love", "meditative", "melancholic", "melodic", "motivational", "movie", "nature", "party", "positive", "powerful", "relaxing", "retro", "romantic", "sad", "sexy", "slow", "soft", "soundscape", "space", "sport", "summer", "trailer", "travel", "upbeat", "uplifting"]

tag = random.choice(tags)
bars = 4
percussion = "With Percussion"
specs = composition_gen_specs

if percussion == "With Percussion":
    specs = with_percussion_specs
elif percussion == "Without Percussion":
    specs = without_percussion_specs
specs.sort(key=lambda x: x.mood_activation_dict[tag], reverse=True)

r = random.randint(0, 19)

top_spec = specs[r]
mean = f"{mean_dict[tag]:.3f}"
std = f"{std_dict[tag]:.3f}"
mult = (top_spec.mood_activation_dict[tag] - mean_dict[tag]) / std_dict[tag]
calc = f"= {mean} + ({mult:.1f} * {std})"
print(f"Rank: {r + 1}   ", tag, "=", top_spec.mood_activation_dict[tag], calc)
print("Notable tags: " + get_notable_tags(top_spec.mood_activation_dict))
rseed = random.randint(0, 1000000)
top_spec.seed = rseed
print("random seed: ", rseed)
bar_duration_ms = top_spec.form_gen_spec.episode_gen_specs[0].bar_structure_gen_spec.bar_start_target_duration_ms
top_spec.form_gen_spec.episode_gen_specs[0].bar_structure_gen_spec.episode_target_duration_ms = bar_duration_ms * bars

generator = CompositionGenerator(top_spec)
composition = generator.generate_composition()

melody_inst_num = top_spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs[3].instrument_num
chord_inst_num = top_spec.form_gen_spec.episode_gen_specs[0].note_sequence_gen_specs[0].instrument_num
melody_inst, _ = SoundfontUtils.get_instrument_name_and_type("SFFluidSynth", melody_inst_num)
chord_inst, _ = SoundfontUtils.get_instrument_name_and_type("SFFluidSynth", chord_inst_num)

part1 = ScorePartGenSpec("Melody", melody_inst, [("treble", [3])])
part2 = ScorePartGenSpec("Chords", chord_inst, [("bass", [0, 1, 2])])
part_gen_specs = [part1, part2]
top_spec.score_gen_spec = ScoreGenSpec(part_gen_specs, True, True)

stem = f"../outputs/regen_excerpts/{tag}_{top_spec.seed}"
IOUtils.save_all_aspects(composition, top_spec, f"{tag.capitalize()} rank {r + 1} ({mult:.2f})", stem)
