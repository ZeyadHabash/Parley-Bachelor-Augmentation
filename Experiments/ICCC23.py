from Parley.Utils.IOUtils import *
import numpy as np

mood_tags = [
  "action", "adventure", "advertising", "background", "ballad", "calm",
  "children", "christmas", "commercial", "cool", "corporate",
  "dark", "deep", "documentary", "drama", "dramatic",
  "dream", "emotional", "energetic", "epic", "fast",
  "film", "fun", "funny", "game", "groovy",
  "happy", "heavy", "holiday", "hopeful", "inspiring",
  "love", "meditative", "melancholic", "melodic", "motivational",
  "movie", "nature", "party", "positive", "powerful",
  "relaxing", "retro", "romantic", "sad", "sexy",
  "slow", "soft", "soundscape", "space", "sport",
  "summer", "trailer", "travel", "upbeat", "uplifting"
]
composition_gen_specs = IOUtils.read_composition_gen_specs("./Parley/Data/excerpts.txt")

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

"""
mood1 = "action"
mood2 = "drama"
mood3 = "uplifting"
happy_ones = filter(lambda x: x.mood_activation_dict[mood1] > mean_dict[mood1] + 2 * (std_dict[mood1]), composition_gen_specs)
scores1 = [x.mood_activation_dict[mood1] for x in composition_gen_specs]
scores2 = [x.mood_activation_dict[mood2] for x in composition_gen_specs]
scores3 = [x.mood_activation_dict[mood3] for x in composition_gen_specs]

scores_list = []
for tag in mood_tags:
  scores_list.append([x.mood_activation_dict[tag] for x in composition_gen_specs])
corr = np.corrcoef(scores_list)
print(len(corr[0]))
# index = np.argmax(corr[0][1:])
# print(index)

# corr = np.corrcoef(scores_list)
# print(corr)
# import seaborn as sns
# sns.heatmap(corr)

mts = [
  "action", "adventure", "background", "calm",
  "dark", "deep", "dramatic",
  "dream", "emotional", "energetic", "epic", "fast",
  "funny", "groovy",
  "happy", "heavy", "hopeful", "inspiring",
  "meditative", "melancholic", "motivational",
  "party", "positive", "powerful",
  "relaxing", "romantic", "sad", "sexy",
  "slow", "soft", "space",
  "summer", "trailer", "upbeat", "uplifting"
]

triples = []
for ind1, mood1 in enumerate(mts):
  for ind2, mood2 in enumerate(mts):
    if ind1 < ind2:
      scores1 = [x.mood_activation_dict[mood1] for x in composition_gen_specs]
      scores2 = [x.mood_activation_dict[mood2] for x in composition_gen_specs]
      corr = np.corrcoef([scores1, scores2])[0][1]
      triples.append((corr, mts[ind1], mts[ind2]))

print("Most negative correlations:")
triples.sort()
for t in triples:
    if t[0] < -0.4:
       print(f"{t[0]:.3f}, {t[1]}, {t[2]}")

print("\nMost positive correlations:")
triples.sort(reverse=True)
for t in triples:
    if t[0] > 0.8:
       print(f"{t[0]:.3f}, {t[1]}, {t[2]}")
    if t[1] == "fast" and t[2] == "slow":
        print(f"{t[0]:.3f}, {t[1]}, {t[2]}")

for threshold_mult in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:

    good_specs = []
    exc_counts = []
    tag_counts_dict = {}
    for tag in mts:
        tag_counts_dict[tag] = 0
    for ind, spec in enumerate(composition_gen_specs):
        exceptional_count = 0
        exceptional_tags = []
        for tag in mts:
            mean = mean_dict[tag]
            std = std_dict[tag]
            activation = spec.mood_activation_dict[tag]
            diff = (activation - mean)/std
            if diff > threshold_mult:
                exceptional_count += 1
                exceptional_tags.append(tag)
                tag_counts_dict[tag] += 1
        exc_counts.append(exceptional_count)
        if exceptional_count > 10:
#            print(ind, exceptional_tags)
            good_specs.append(spec)

    total_specs = len(composition_gen_specs)
    print("=======")
    print("threshold:", threshold_mult)
    print("number of excerpts with 10 or more exceptional tags:", f"{100 * (len(good_specs)/total_specs):.2f}")
    #print(exc_counts)
    #print(tag_counts_dict)

    pairs = []
    for tag in mts:
        pairs.append((tag_counts_dict[tag], tag))

    pairs.sort(reverse=True)
    #for p in pairs:
    #    print(p)

    print(f"Most used tag ({pairs[0][1]}):", f"{100 * pairs[0][0]/total_specs:.2f}")
    print(f"Least used tag ({pairs[-1][1]}):", f"{100 * pairs[-1][0]/total_specs:.2f}")

    zeros = []
    for e in exc_counts:
        if e == 0:
            zeros.append(e)
    print("Number of un-tagged excerpts:", f"{100 * len(zeros)/total_specs:.2f}")

    print("Average number of exceptional tags:", f"{np.mean(exc_counts):.2f}")

print(len(composition_gen_specs))


"""


from Parley.CompositionSpecs.Flaneur import *
do_flaneur_experiments()
