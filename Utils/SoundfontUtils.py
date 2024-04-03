import random
from Parley.Specifications.InstrumentNums import *

class SoundfontUtils:

    def get_instrument_name_and_type(soundfont_class_name, instrument_num):
        klass = globals()[soundfont_class_name]
        soundfont = klass()
        for a in dir(soundfont):
            sa = f"{a}"
            if "__" not in sa and sa != "num_instruments":
                if getattr(soundfont, a) == instrument_num:
                    parts = a.split("_")
                    s = ""
                    for p in parts[1:]:
                        s += p + " "
                    return s.strip(), parts[0]
        return None

    def get_random_instrument_num(soundfont_class_name, instrument_types=None):
        klass = globals()[soundfont_class_name]
        soundfont = klass()
        if instrument_types is None:
            return random.randint(0, soundfont.num_instruments - 1)
        else:
            inst_num = random.randint(0, soundfont.num_instruments - 1)
            _, type = SoundfontUtils.get_instrument_name_and_type(soundfont_class_name, inst_num)
            if type in instrument_types:
                return inst_num
            else:
                return SoundfontUtils.get_random_instrument_num(soundfont_class_name, instrument_types)