from Parley.Utils.MathUtils import *
from dataclasses import dataclass
import copy
import numpy as np


@dataclass
class AnalysisClass:
    values: []
    counts: {}
    props: {}
    modes: []
    len: 0; min: 0; mean: 0; max: 0
    entropy: 0


class DataUtils:

    def get_analysis_details(values):
        counts = {}
        props = {}
        for val in sorted(values):
            counts[val] = 1 if val not in counts else counts[val] + 1
            props[val] = counts[val]/len(values)
        max_count = 0 if len(values) == 0 else max([counts[val] for val in values])
        modes = [] if len(values) == 0 else [x for x in counts.keys() if counts[x] == max_count]
        if len(values) > 0:
            return AnalysisClass(values=values, counts=counts, props=props, modes=modes,
                                 len=len(values), min=min(values), mean=np.mean(values), max=max(values),
                                 entropy=MathUtils.get_entropy(values))
        else:
            return AnalysisClass([], {}, {}, [], 0, 0, 0, 0, 0)

    def analysis_object_string(obj):
        props_string = "{"
        for key in obj.props.keys():
            props_string += f"{key}: {obj.props[key]:.3f}, "
        props_string = props_string[0:-2] + "}"
        return f"len:{obj.len:.3f} min:{obj.min:.3f} mean:{obj.mean:.3f} max:{obj.max:.3f} entropy:{obj.entropy:.3f} counts:{obj.counts} props:{props_string} modes:{obj.modes}"

    def dataobject_string(dataobject):
        s = ""
        keys = sorted(list(dataobject.__dict__.keys()))
        max_len = 3 + max([len(key) for key in keys])
        for key in keys:
            sep = " " * (max_len - len(key))
            obj = dataobject.__dict__[key]
            if isinstance(obj, AnalysisClass):
                if len(obj.counts) == 0:
                    s += f"{key}{sep}n/a\n"
                else:
                    s += f"{key}{sep}{DataUtils.analysis_object_string(obj)}\n"
            else:
                s += f"{key}={dataobject.__dict__[key]}\n"
        return s

    def get_analysis_details_average(objs):
        all_values = [obj.values for obj in objs]
        all_modes = [obj.modes for obj in objs]
        av_len = np.mean([obj.len for obj in objs])
        av_min = np.mean([obj.min for obj in objs])
        av_mean = np.mean([obj.mean for obj in objs])
        av_max = np.mean([obj.max for obj in objs])
        av_entropy = np.mean([obj.entropy for obj in objs])
        total_num_values = 0
        all_counts_lists_dict = {}
        for obj in objs:
            for key in obj.counts:
                total_num_values += obj.counts[key]
                counts_list = [] if key not in all_counts_lists_dict else all_counts_lists_dict[key]
                counts_list.append(obj.counts[key])
                all_counts_lists_dict[key] = counts_list
        props_list_dict = {}
        counts_list_dict = {}
        for key in all_counts_lists_dict:
            counts_list_dict[key] = np.mean(all_counts_lists_dict[key])
            props_list_dict[key] = counts_list_dict[key]/(total_num_values/len(objs))

        return AnalysisClass(all_values, counts_list_dict, props_list_dict, all_modes, av_len, av_min, av_mean, av_max, av_entropy)

    def get_average_dataobject(dataobjects):
        vals_dict = {}
        for d in dataobjects:
            for key in d.__dict__:
                vals = [] if key not in vals_dict else vals_dict[key]
                vals.append(d.__dict__[key])
                vals_dict[key] = vals
        c = copy.deepcopy(dataobjects[0])
        for attr in dir(c):
            if "__" not in attr:
                if isinstance(getattr(c, attr), int) or isinstance(getattr(c, attr), float):
                    setattr(c, attr, np.mean(vals_dict[attr]))
                if isinstance(getattr(c, attr), AnalysisClass):
                    setattr(c, attr, DataUtils.get_analysis_details_average(vals_dict[attr]))
        return c
