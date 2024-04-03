import itertools
import random
from Parley.Utils.ChordUtils import *


class MelodyUtils:

    def map_to_closest_in_key(key_sig, pitch):
        pitch_classes = ChordUtils.pitch_classes_for_key_sig(key_sig)
        try_pitches = []
        if ChordUtils.pitch_class(pitch + 1) in pitch_classes:
            try_pitches.append(pitch + 1)
        if ChordUtils.pitch_class(pitch - 1) in pitch_classes:
            try_pitches.append(pitch - 1)

        #TODO FIX THIS!!!

        if len(try_pitches) == 0:
            return pitch

        return random.choice(try_pitches)

    def homogenise_tied_notes(all_notes, note):
        stop_now = False
        ind = all_notes.index(note) + 1
        while ind < len(all_notes) and not stop_now:
            next_note = all_notes[ind]
            if next_note.tie_type == "mid" or next_note.tie_type == "end":
                next_note.pitch = note.pitch
                next_note.score_colour = note.score_colour
            else:
                stop_now = True
            ind += 1

    def get_same_pitch_neighbourhood(all_notes, note):
        neighbourhood = [note]
        ind = all_notes.index(note)
        back_note = None if ind == 0 else all_notes[ind - 1]
        while back_note is not None and back_note.pitch == note.pitch:
            neighbourhood.insert(0, back_note)
            ind = ind - 1
            back_note = None if ind == 0 else all_notes[ind - 1]
        ind = all_notes.index(note)
        next_note = None if (ind == (len(all_notes) - 1)) else all_notes[ind + 1]
        while next_note is not None and next_note.pitch == note.pitch:
            neighbourhood.append(next_note)
            ind = ind + 1
            next_note = None if (ind == (len(all_notes) - 1)) else all_notes[ind + 1]
        return neighbourhood

    def closest_pitch_to_neighbours_for_pitch_class(target_pitch, pitch_class, prev_pitch, next_pitch):
        target_pitch_class = ChordUtils.pitch_class(target_pitch)
        diff = pitch_class - target_pitch_class
        posses = [target_pitch + diff, target_pitch + diff - 12, target_pitch + diff + 12]
        min_dist = 100000
        closest_pitch = posses[0]
        for poss in posses:
            dist1 = 0 if prev_pitch is None else abs(poss - prev_pitch)
            dist2 = 0 if next_pitch is None else abs(poss - next_pitch)
            dist = dist1 + dist2
            if dist < min_dist:
                min_dist = dist
                closest_pitch = poss
        return closest_pitch

    def closest_pitch_for_pitch_class(target_pitch, pitch_class):
        target_pitch_class = ChordUtils.pitch_class(target_pitch)
        diff = pitch_class - target_pitch_class
        posses = [target_pitch + diff, target_pitch + diff - 12, target_pitch + diff + 12]
        min_dist = 100000
        closest_pitch = posses[0]
        for poss in posses:
            dist = abs(poss - target_pitch)
            if dist < min_dist:
                min_dist = dist
                closest_pitch = poss
        return closest_pitch

    def get_backbone_sequences(chord, num_notes, octave_offset):
        offset_pitches = [x + (12 * octave_offset) for x in chord.pitches]
        all_permutations = list(itertools.permutations(offset_pitches, len(chord.pitches)))
        l = len(all_permutations[0])
        while l < num_notes:
            l += len(all_permutations[0])
            next_all_permutations = []
            for p in all_permutations:
                for q in all_permutations:
                    next_p = list(p).copy()
                    if next_p[-1] != q[0]:
                        next_p.extend(q)
                        next_all_permutations.append(next_p)
            all_permutations = next_all_permutations
        sequences = []
        for p in all_permutations:
            sequences.append(p[0:num_notes])
        return sequences

    def random_from_top_bracket(sequences, target_pitch, allow_target_pitch):
        pairs = []
        for s in sequences:
            measures = [MelodyUtils.start_distance(s, target_pitch, allow_target_pitch), MelodyUtils.roughness(s)]
            pairs.append([measures, s])
        pairs.sort()
        top_bracket = []
        top_measures = pairs[0][0]
        measures = pairs[0][0]
        pos = 0
        while pos < len(pairs) - 1 and measures == top_measures:
            top_bracket.append(pairs[pos][1])
            pos += 1
            measures = pairs[pos][0]
        random_sequence = random.choice(top_bracket)
        return random_sequence

    def start_distance(sequence, target_pitch, allow_target_pitch):
        if target_pitch is None:
            return 0
        if not allow_target_pitch and sequence[0] == target_pitch:
            return 1000
        return abs(sequence[0] - target_pitch)

    def roughness(sequence):
        roughness = 0
        for i in range(1, len(sequence)):
            roughness += abs(sequence[i] - sequence[i-1])
        return roughness

    def get_passing_note_pitches(start_note, end_pitch, key_sig, policy):

        if end_pitch is None or start_note.pitch == end_pitch:
            return [start_note.pitch]

        direction = 1 if end_pitch > start_note.pitch else -1
        current_pitch = start_note.pitch
        passing_note_pitches = [current_pitch]
        previous_pitch = current_pitch
        current_pitch += direction
        while current_pitch != end_pitch:
            if key_sig is None:
                if abs(previous_pitch - current_pitch) > 1:
                    passing_note_pitches.append(current_pitch)
                    previous_pitch = current_pitch
            elif ChordUtils.note_is_in_key(current_pitch, key_sig):
                passing_note_pitches.append(current_pitch)
            current_pitch += direction
        if policy == "mid":
            if len(passing_note_pitches) <= 2:
                return passing_note_pitches
            if len(passing_note_pitches) % 2 == 1:
                pos = len(passing_note_pitches)//2
                return [start_note.pitch, passing_note_pitches[pos]]
            else:
                pos = len(passing_note_pitches)//2 if bool(random.getrandbits(1)) else len(passing_note_pitches)//2 - 1
                return [start_note.pitch, passing_note_pitches[pos]]
        return passing_note_pitches
