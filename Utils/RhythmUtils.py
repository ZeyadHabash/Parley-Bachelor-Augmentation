from Parley.Utils.ChordUtils import *
from Parley.Utils.MathUtils import *
from Parley.Specifications.Artefacts import *
import random
import itertools


class RhythmUtils:

    def get_overlap_ticks(note1, note2):
        r1 = [note1.start_tick, note1.start_tick + note1.duration_ticks]
        r2 = [note2.start_tick, note2.start_tick + note2.duration_ticks]
        return MathUtils.get_overlap(r1, r2)

    def correct_note_sequence(note_sequence):
        notes = note_sequence.notes
        note_sequence_ticks = sum([n.duration_ticks for n in notes])
        bar_duration_ticks = note_sequence.notes[0].parent_bar.duration_ticks
        addon = 1 if note_sequence_ticks < bar_duration_ticks else -1
        while note_sequence_ticks != bar_duration_ticks:
            ind = random.randint(0, len(notes) - 1)
            notes[ind].duration_ticks += addon
            for i in range(ind + 1, len(notes)):
                notes[i].start_tick += addon
            note_sequence_ticks += addon

    def get_start_duration_ticks(total_duration_ticks, rhythm_string):
        details = []
        p_hash = {}
        for p in rhythm_string.split(","):
            start_numerator = int(p.split(":")[1].split("/")[0])
            p_hash[start_numerator] = p
        denominator = int(rhythm_string.split(",")[0].split(":")[1].split("/")[1])
        mult = int(128/denominator)
        numerator = 1
        while numerator <= denominator:
            if numerator in p_hash:
                part = p_hash[numerator]
                bits = part.split(":")
                start_frac = RhythmUtils.get_frac(bits[1], True)
                top_start_frac = int(bits[1].split("/")[0])
                duration_frac = RhythmUtils.get_frac(bits[2], False)
                start_tick = int(round(total_duration_ticks * start_frac))
                duration_ticks = int(round(total_duration_ticks * duration_frac))
                top_duration_frac = int(bits[2].split("/")[0])
                details.append([int(bits[0]), start_tick, duration_ticks, (top_start_frac - 1) * mult, top_duration_frac * mult])
                numerator += top_duration_frac
            else:
                start_numerator = numerator
                while numerator not in p_hash and numerator <= denominator:
                    numerator += 1
                start_frac = (start_numerator - 1)/denominator
                start_tick = int(round(total_duration_ticks * start_frac))
                top_duration_frac = numerator - start_numerator
                duration_ticks = int(round((top_duration_frac/denominator) * total_duration_ticks))
                details.append([-1, start_tick, duration_ticks, (start_numerator - 1) * mult, top_duration_frac * mult])
        return details

    def get_frac(frac_string, minus_1):
        parts = frac_string.split("/")
        takeoff = 1 if minus_1 else 0
        return (float(parts[0]) - takeoff)/float(parts[1])

    def quantize(episode, track_num):
        bar_subseq_hash = {}
        for bar in episode.bars:
            if bar.track_divisions_hash is None:
                bar.track_divisions_hash = {}
            subseqs_to_quantize = []
            bar_subseq_hash[bar] = subseqs_to_quantize
            for note_sequence in bar.note_sequences:
                if note_sequence.track_num == track_num:
                    subseq_to_quantize = []
                    for note in note_sequence.notes:
                        if note.is_backbone_starter:
                            if len(subseq_to_quantize) > 0:
                                subseqs_to_quantize.append(subseq_to_quantize)
                                subseq_to_quantize = []
                        subseq_to_quantize.append(note)
                    if len(subseq_to_quantize) > 0:
                        subseqs_to_quantize.append(subseq_to_quantize)

        for ind, bar in enumerate(episode.bars):
            subseqs_to_quantize = bar_subseq_hash[bar]
            for m in [1, 2, 4, 8, 16, 32, 64, 128]:
                good_for_all = True
                for subseq in subseqs_to_quantize:
                    c = len(subseq)
                    n = subseq[0].parent_chord.num_fracs
                    d = subseq[0].parent_chord.frac
                    if (c/m > n/d):
                        good_for_all = False
                if good_for_all:
                    bar.track_divisions_hash[track_num] = m
                    break

        for ind, bar in enumerate(episode.bars):
            division_duration_ticks = int(bar.duration_ticks//bar.track_divisions_hash[track_num])
            subseqs_to_quantize = bar_subseq_hash[bar]
            start_frac = 0
            for subseq in subseqs_to_quantize:
                RhythmUtils.quantize_subseq(subseq, bar.track_divisions_hash[track_num], division_duration_ticks)
                for note in subseq:
                    note.start_frac = start_frac
                    note.start_tick = bar.start_tick + int(round(bar.duration_ticks * start_frac/128))
                    start_frac += note.num_fracs

    def quantize_subseq(subseq, num_divisions, division_duration_ticks):
        addon = int(128/num_divisions)
        backbone_notes = []
        for ind, note in enumerate(subseq):
            if ChordUtils.pitch_is_backbone_for_chord(note.pitch, note.parent_chord):
                backbone_notes.append(note)
            note.duration_ticks = division_duration_ticks
            note.num_fracs = addon

        total_ticks = len(subseq) * division_duration_ticks
        chord_ticks = subseq[0].parent_chord.duration_ticks
        while total_ticks + division_duration_ticks <= chord_ticks:
            note = random.choice(backbone_notes)
            note.duration_ticks += division_duration_ticks
            note.num_fracs += addon
            total_ticks += division_duration_ticks

        while total_ticks + 1 <= chord_ticks:
            note = random.choice(backbone_notes)
            note.duration_ticks += 1
            total_ticks += 1

    def get_bar_divisions(rhythm_string):
        denominators = []
        for part in rhythm_string.split(","):
            bits = part.split(":")
            denominators.append(int(bits[2].split("/")[1]))
        return max(denominators)

    def get_note_quantization_split(num_fracs, so_far=[]):
        wholes = [1, 2, 4, 8, 16, 32, 64, 128]
        dotted = [round(x * 1.5) for x in wholes[1:-1]]
        double_dotted = [round(x * 1.75) for x in wholes[2:-1]]
        all = wholes.copy()
        all.extend(dotted)
        all.extend(double_dotted)
        all.sort()
        so_far_copy = so_far.copy()
        if num_fracs in wholes:
            so_far_copy.append((num_fracs, 0))
            return so_far_copy
        if num_fracs in dotted:
            so_far_copy.append((int(num_fracs/1.5), 1))
            return so_far_copy
        if num_fracs in double_dotted:
            so_far_copy.append((int(num_fracs/1.75), 2))
            return so_far_copy

        """
        for a in all:
            if a == num_fracs:
                if a in wholes:
                    so_far_copy.append((a, 0))
                if a in dotted:
                    so_far_copy.append((wholes[dotted.index(a) + 1], 1))
                if a in double_dotted:
                    so_far_copy.append((wholes[double_dotted.index(a) + 2], 2))
                return so_far_copy
        """

        for ind, w in enumerate(wholes):
            if w > num_fracs:
                next_so_far = so_far.copy()
                next_so_far.append((wholes[ind - 1], 0))
                return RhythmUtils.get_note_quantization_split(num_fracs - wholes[ind - 1], next_so_far)

        # TODO!!!! make ticks add up to bar

    def get_best_beat_ordering(dur_dot_pairs, start_frac):
        permutations = itertools.permutations(dur_dot_pairs)
        pairs = []
        beats = [0, 32, 64, 96]
        half_beats = [16, 48, 80, 112]
        for ddp in permutations:
            beat_frac = start_frac
            score = 0
            for dur, _ in ddp:
                for b in beats:
                    if beat_frac == b:
                        score += 2
                for b in half_beats:
                    if beat_frac == b:
                        score += 1
                beat_frac += dur
            pairs.append((score, ddp))
        pairs.sort(reverse=True)
        return pairs[0][1]

    def get_backbone_passing_note_signature(note_sequence):
        s = ""
        for note in note_sequence.notes:
            note_type = "b" if note.is_backbone_note else "p"
            s += note_type
        return s

    def copy_rhythm_onto(note_sequence1, note_sequence2):
        for ind, note1 in enumerate(note_sequence1.notes):
            note2 = note_sequence2.notes[ind]
            note2.start_tick = int(round((note1.start_tick/note1.parent_bar.duration_ticks) * note2.parent_bar.duration_ticks))
            old_duration_ticks = note2.duration_ticks
            note2.duration_ticks = int(round((note1.duration_ticks/note1.parent_bar.duration_ticks) * note2.parent_bar.duration_ticks))
            diff = note2.duration_ticks - old_duration_ticks
            if note2.tie_type == "start":
                note2.tied_duration_ticks += diff
            note2.start_frac = note1.start_frac
            note2.num_fracs = note1.num_fracs
            note2.cutoff_prop = note1.cutoff_prop