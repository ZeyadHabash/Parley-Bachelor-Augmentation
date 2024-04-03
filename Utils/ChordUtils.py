import random


note_letters = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
major_scale_positions = [0, 2, 4, 5, 7, 9, 11]
minor_scale_positions = [0, 2, 3, 5, 7, 8, 10]


class ChordUtils:

    def get_octave(pitch):
        return pitch//12 - 1

    def pitch_class(pitch):
        return pitch % 12

    def get_chord_name(chord):
        pitch_classes = ChordUtils.pitch_classes_for_chord(chord)
        for letter in note_letters:
            for mm  in ["maj", "min"]:
                chord_name = letter + mm
                scale_pitch_classes = ChordUtils.pitch_classes_for_key_sig(chord_name)
                maj_cpc = [scale_pitch_classes[0], scale_pitch_classes[2], scale_pitch_classes[4]]
                if len([x for x in pitch_classes if x in maj_cpc]) == 3:
                    return chord_name
        return ""

    def are_same_pitch_classes(pitches1, pitches2):
        pitch_classes1 = [ChordUtils.pitch_class(p) for p in pitches1]
        for pitch in pitches2:
            if ChordUtils.pitch_class(pitch) not in pitch_classes1:
                return False
        return True

    def pitch_classes_for_chord(chord):
        pitch_classes = []
        for pitch in chord.pitches:
            pitch_classes.append(ChordUtils.pitch_class(pitch))
        return pitch_classes

    def pitch_classes_for_key_sig(key_sig):
        tonic_letter = key_sig.split("maj")[0] if "maj" in key_sig else key_sig.split("min")[0]
        scale_positions = major_scale_positions if "maj" in key_sig else minor_scale_positions
        pitch_classes = []
        tonic_pitch_class = note_letters.index(tonic_letter)
        for pos in scale_positions:
            pitch_classes.append((tonic_pitch_class + pos) % 12)
        return pitch_classes

    def pitch_is_backbone_for_chord(pitch, chord):
        pc = ChordUtils.pitch_class(pitch)
        for cp in chord.pitches:
            pc2 = ChordUtils.pitch_class(cp)
            if pc2 == pc:
                return True
        return False

    def get_interval(pitch1, pitch2):
        pitch_class1 = ChordUtils.pitch_class(pitch1)
        pitch_class2 = ChordUtils.pitch_class(pitch2)
        dist = abs(pitch_class1 - pitch_class2)
        return min(dist, 12-dist)

    def is_nrt_admissible(pitches):
        pitch_classes = [ChordUtils.pitch_class(a) for a in pitches]
        pairs = []
        for i in range(0, len(pitch_classes)):
            for j in range(i + 1, len(pitch_classes)):
                pairs.append([pitch_classes[i], pitch_classes[j]])
        for pair in pairs:
            if abs(pair[0] - pair[1]) <= 1:
                return False
            if abs(pair[0] + 12 - pair[1]) <= 1:
                return False
            if abs(pair[0] - 12 - pair[1]) <= 1:
                return False
        return True

    def is_major(pitches):
        a, b, c = ChordUtils.mapped_to_mid_octave(pitches)
        for t1, t2, t3 in [[a, b, c], [c - 12, a, b], [b - 12, c - 12, a]]:
            if t2 - t1 == 4 and t3 - t2 == 3:
                return True
        return False

    def is_minor(pitches):
        a, b, c = ChordUtils.mapped_to_mid_octave(pitches)
        for t1, t2, t3 in [[a, b, c], [c - 12, a, b], [b - 12, c - 12, a]]:
            if t2 - t1 == 3 and t3 - t2 == 4:
                return True
        return False

    def is_major_or_minor(pitches):
        return ChordUtils.is_major(pitches) or ChordUtils.is_minor(pitches)

    def satisfies_majmin_constraint(pitches, majmin_constraint):
        if majmin_constraint is None:
            return True
        if majmin_constraint == "maj" and ChordUtils.is_major(pitches):
            return True
        if majmin_constraint == "min" and ChordUtils.is_minor(pitches):
            return True
        if majmin_constraint == "majmin" and ChordUtils.is_major_or_minor(pitches):
            return True
        return False

    def chord_is_in_key(pitches, key_sig):
        if key_sig == None:
            return True
        pitch_classes = ChordUtils.pitch_classes_for_key_sig(key_sig)
        for pitch in pitches:
            if ChordUtils.pitch_class(pitch) not in pitch_classes:
                return False
        return True

    def note_is_in_key(pitch, key_sig):
        return ChordUtils.pitch_class(pitch) in ChordUtils.pitch_classes_for_key_sig(key_sig)

    def mapped_to_mid_octave(pitches):
        mapped_pitches = []
        for pitch in pitches:
            try_pitch = pitch + (12 * 5)
            mapped_pitch = pitch
            while try_pitch > 0:
                if try_pitch >= 60 and try_pitch < 72:
                    mapped_pitch = try_pitch
                    break
                try_pitch -= 12
            mapped_pitches.append(mapped_pitch)
        mapped_pitches.sort()
        return mapped_pitches

    def map_pitch_to_focal_pitch(pitch, focal_pitch):
        return ChordUtils.mapped_to_focal_pitch([pitch], focal_pitch)[0]

    def mapped_to_focal_pitch(pitches, focal_pitch):
        min_dist = 1000000
        mapped_pitches = []
        for pitch in pitches:
            min_dist = 10000
            try_pitch = pitch + (12 * 5)
            mapped_pitch = pitch
            while try_pitch > 0:
                dist = abs(focal_pitch - try_pitch)
                if dist < min_dist:
                    mapped_pitch = try_pitch
                    min_dist = dist
                try_pitch -= 12
            mapped_pitches.append(mapped_pitch)
        mapped_pitches.sort()
        return mapped_pitches

    def get_suitable_chord_pitches(fixed_key_sig, majmin_constraint, focal_pitch):
        is_ok = False
        while not is_ok:
            pitches = []
            while len(pitches) < 3:
                pitch = random.randint(focal_pitch - 6, focal_pitch + 5)
                is_ok = True
                for p in pitches:
                    pc_distance = abs(ChordUtils.pitch_class(p) - ChordUtils.pitch_class(pitch))
                    if pc_distance <= 1 or pc_distance == 11:
                        is_ok = False
                if is_ok:
                    pitches.append(pitch)
            is_ok = True
            if fixed_key_sig is not None and not ChordUtils.chord_is_in_key(pitches, fixed_key_sig):
                is_ok = False
            if majmin_constraint == "maj" and not ChordUtils.is_major(pitches):
                is_ok = False
            if majmin_constraint == "min" and not ChordUtils.is_minor(pitches):
                is_ok = False
            if majmin_constraint == "majmin" and not ChordUtils.is_major_or_minor(pitches):
                is_ok = False
        return pitches
