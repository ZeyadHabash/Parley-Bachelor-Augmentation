import random
from Parley.Utils.ChordUtils import *


class NROUtils:

    def get_all_nros():
        moves = range(-2, 3)
        all_nros = [[]]
        for rep in range(0, 3):
            new_nros = []
            for nro in all_nros:
                for move in moves:
                    new_nro = nro.copy()
                    new_nro.append(move)
                    new_nros.append(new_nro)
            all_nros = new_nros
        final_nros = []
        for [a, b, c] in all_nros:
            if 0 in [a, b, c]:
                if a is not b or a is not c or b is not c:
                    final_nros.append([a, b, c])
        return final_nros

    all_nros = get_all_nros()

    def get_random_admissible_cnro(trichord_pitches, min_cnro_len, max_cnro_len,
                                   fixed_key_sig, majmin_constraint):
        trial_num = 0
        is_ok = False
        while is_ok is False and trial_num < 1000:
            cnro_len = random.randint(min_cnro_len, max_cnro_len)
            cnro = [0, 0, 0]
            for i in range(0, cnro_len):
                nro = random.choice(NROUtils.all_nros)
                for j in range(0, 3):
                    cnro[j] += nro[j]
            new_pitches = trichord_pitches.copy()
            for i in range(0, len(cnro)):
                new_pitches[i] += cnro[i]
            is_ok = (ChordUtils.is_nrt_admissible(new_pitches)
                     and ChordUtils.satisfies_majmin_constraint(new_pitches, majmin_constraint)
                     and ChordUtils.chord_is_in_key(new_pitches, fixed_key_sig))
            trial_num += 1
        if trial_num >= 1000:
            return NROUtils.get_random_admissible_cnro(trichord_pitches, min_cnro_len, max_cnro_len + 1,
                                                       fixed_key_sig, majmin_constraint)
        return cnro, new_pitches
