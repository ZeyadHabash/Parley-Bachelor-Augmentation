from Parley.Specifications.Specifications import *
from Parley.Specifications.InstrumentNums import * # (Need this - don't delete)
import random


class SpecUtils:

    def get_instantiated_copy(spec, bar):
        return SpecUtils.spec_copy(spec, True, bar)

    def spec_string(spec, num_tabs=0):
        var_type = type(spec).__name__
        t = "   " * num_tabs
        if var_type == "NoneType":
            return "None"
        if var_type == "method":
            return ""
        if var_type == "dict":
            return spec.copy()
        if var_type == "bool" or var_type == "int" or var_type == "float" or var_type == "string" or var_type == "str":
            return f"{spec}"
        if var_type == "list":
            s = ""
            for v in spec:
                s += SpecUtils.spec_string(v, num_tabs + 1) + "\n"
            return s
        else:
            # klass = globals()[var_type]
            s = f"{t}{var_type}\n"
            for a in dir(spec):
                if ("__" not in a):
                    val = getattr(spec, a)
                    val_string = SpecUtils.spec_string(val, num_tabs + 1)
                    if val_string != "":
                        s += f"{t}{a} = {val_string}\n"
            return s.strip()

    def val_copy(val, var_type, make_instantiation=False, bar=None):
        if make_instantiation and var_type == "str":
            return SpecUtils.val_instantiation(val, bar)
        if var_type == "bool" or var_type == "int" or var_type == "float" or var_type == "string" or var_type == "str":
            return val
        elif var_type == "dict":
          d = {}
          for k in val.keys():
            d[k] = val[k]
          return d
        elif var_type == "list":
            l = []
            for v in val:
                l.append(SpecUtils.spec_copy(v, make_instantiation, bar))
            return l

    def val_instantiation(val, bar):
        cb_num = bar.comp_bar_num
        eb_num = bar.ep_bar_num
        cbcs = {}
        ebcs = {}
        cbps = []
        ebps = []
        pcs = []
        others = []
        for part in val.split(" "):
            if "(" in part and ")" in part:
                instantiation = SpecUtils.read_val_from_string(part.split("(")[0])
                bracket_vals = part.split("(")[1][:-1].split(",")
                for bval in bracket_vals:
                    counter_num = None if "=" not in bval else SpecUtils.read_val_from_string(bval.split("=")[1])
                    if "cb=" in bval:
                        if counter_num == cb_num:
                            return instantiation
                        if counter_num < 0 and (bar.num_bars_to_comp_end - 1) == counter_num:
                            return instantiation
                    elif "eb=" in bval:
                        if counter_num == eb_num:
                            return instantiation
                        if counter_num < 0 and (bar.num_bars_to_ep_end - 1) == counter_num:
                            return instantiation
                    elif "cbc=" in bval:
                        cbcs[counter_num] = instantiation
                    elif "ebc=" in bval:
                        ebcs[counter_num] = instantiation
                    elif "pc=" in bval:
                        pcs.append((counter_num, instantiation))
                    elif "cbp=" in bval:
                        cbps.append((counter_num, instantiation))
                    elif "ebp=" in bval:
                        ebps.append((counter_num, instantiation))
            else:
                others.append(SpecUtils.read_val_from_string(part))
        instantiated_val = None
        if len(cbcs.keys()) > 0:
            instantiated_val = SpecUtils.get_cycle_val(cbcs, cb_num)
        if instantiated_val is None and len(ebcs.keys()) > 0:
            instantiated_val = SpecUtils.get_cycle_val(ebcs, eb_num)
        if instantiated_val is None and len(cbps) > 0:
            instantiated_val = SpecUtils.get_pos_val(cbps, bar)
        if instantiated_val is None and len(ebps) > 0:
            instantiated_val = SpecUtils.get_pos_val(ebps, bar)
        if instantiated_val is None and len(pcs) > 0:
            instantiated_val = SpecUtils.get_prob_val(pcs)
        if instantiated_val is not None:
            return instantiated_val
        if len(others) == 0:
            return None
        return random.choice(others)

    def get_cycle_val(cs, counter):
        max_cbc = max(list(cs.keys())) + 1
        cycle_counter = counter % max_cbc
        if cycle_counter in cs:
            return cs[cycle_counter]
        return None

    def get_pos_val(ps, bar):
        total_ep_bars = bar.ep_bar_num + bar.num_bars_to_ep_end
        frac = bar.ep_bar_num / total_ep_bars
        last_ind = 0
        for ind, pair in enumerate(ps):
            if frac == pair[0]:
                return pair[1]
            if frac >= pair[0]:
                last_ind = ind
        dist = ps[last_ind + 1][0] - ps[last_ind][0]
        ffrac = (frac - ps[last_ind][0]) / dist
        instantiation = int(round(((1 - ffrac) * ps[last_ind][1]) + (ffrac * ps[last_ind + 1][1])))
        return instantiation

    def get_prob_val(pcs):
        triples = []
        low = 0
        for pc, v in pcs:
            high = low + pc
            triples.append((low, high, v))
            low += pc
        r = random.randint(0, triples[-1][1] - 1)
        for triple in triples:
            if triple[0] <= r < triple[1]:
                return triple[2]
        return None

    def read_val_from_string(val):
        if val == "none" or val == "None":
            return None
        if val == "False":
            return False
        if val == "True":
            return True
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

    def spec_copy(spec, make_instantiation=False, bar=None):
        var_type = type(spec).__name__
        if var_type == "NoneType":
            return None
        if var_type == "method":
            return spec
        if var_type == "dict" or var_type == "bool" or var_type == "list" or var_type == "int" or var_type == "float" or var_type == "string" or var_type == "str":
            return SpecUtils.val_copy(spec, var_type, make_instantiation, bar)
        else:
            klass = globals()[var_type]
            copy = klass()
            for a in dir(spec):
                if ("__" not in a):
                    val = getattr(spec, a)
                    attr_name = type(val).__name__
                    setattr(copy, a, SpecUtils.spec_copy(val, make_instantiation, bar))
            return copy
