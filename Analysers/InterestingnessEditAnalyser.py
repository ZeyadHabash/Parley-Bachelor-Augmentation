from Parley.Utils.DataUtils import *
from Parley.Utils.AnalysisUtils import *
from Parley.Utils.ExtractionUtils import *


class InterestingnessEditAnalyser:

    def __init__(self, analyser_spec):
        self.analyser_spec = analyser_spec

    def analyseComposition(self, composition):
        bars = ExtractionUtils.get_bar_notes_for_track(composition, self.analyser_spec.track_num)
        triples = []
        for bar_ind, bar in enumerate(bars):
            total_improvement = sum([note.edit_improvement for note in bar if note.edit_improvement is not None and (note.tie_type is None or note.tie_type == "start")])
            total_improvement /= len(bars)
            if len(bar) > self.analyser_spec.min_num_notes:
                triples.append((total_improvement, bar_ind, bar))
        triples.sort(reverse=True)
        bar_inds = []
        for triple in triples[0:self.analyser_spec.num_highlight_passages]:
            bar = triple[2][0].parent_bar
            bar.score_notes.append(ScoreNote("most improved", "green"))
            bar_inds.append(triple[1])
            if self.analyser_spec.make_notes_purple:
                for note in triple[2]:
                    note.score_colour = "purple"
        return bar_inds