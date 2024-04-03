from Parley.Utils.XMLUtils import *
from Parley.Utils.RhythmUtils import *


class ScoreGenerator:

    def __init__(self, score_gen_spec):
        self.score_gen_spec = score_gen_spec
        self.doc = None
        self.root = None
        self.letters = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.note_types_hash = {128: "whole", 64: "half", 32: "quarter", 16: "eighth",
                                8: "16th", 4: "32nd", 2: "64th", 1: "128th"}

    def create_score(self, musicxml_filepath, composition, opus):
        self.doc, self.root = XMLUtils.get_doc_and_root("score-partwise", {"version": "4.0"})
        work_elem = XMLUtils.add_child(self.doc, self.root, "work")
        XMLUtils.add_child(self.doc, work_elem, "work-number", {}, opus)
        XMLUtils.add_child(self.doc, work_elem, "work-title", {}, composition.title)
        identification_elem = XMLUtils.add_child(self.doc, self.root, "identification")
        XMLUtils.add_child(self.doc, identification_elem, "creator", {"type": "composer"}, "Parley")
        part_list_elem = XMLUtils.add_child(self.doc, self.root, "part-list")
        for part_ind, part_spec in enumerate(self.score_gen_spec.part_gen_specs):
            part_id = f"P{part_ind + 1}"
            score_part_elem = XMLUtils.add_child(self.doc, part_list_elem, "score-part", {"id": part_id})
            XMLUtils.add_child(self.doc, score_part_elem, "part-name", {}, part_spec.part_name)
            self.add_part(part_spec, composition, part_ind, part_id)
        doc_string = XMLUtils.prettify(self.doc)
        f = open(musicxml_filepath, "w")
        f.write(doc_string)
        f.close()

    def add_part(self, part_spec, composition, part_ind, part_id):
        part_elem = XMLUtils.add_child(self.doc, self.root, "part", {"id": part_id})
        bar_ind = 1
        for episode_num, episode in enumerate(composition.form.episodes):
            for bar in episode.bars:
                is_start_of_episode = (episode.bars.index(bar) == 0)
                measure_elem = self.add_measure(part_spec, part_ind, bar_ind, part_elem, bar, is_start_of_episode, episode_num, episode.title)
                for staff_num, (clef, track_nums) in enumerate(part_spec.clef_track_list):
                    if staff_num > 0:
                        backup_elem = XMLUtils.add_child(self.doc, measure_elem, "backup")
                        XMLUtils.add_child(self.doc, backup_elem, "duration", {}, "128")
                    note_sequences_for_bar = []
                    for note_sequence in bar.note_sequences:
                        if note_sequence.track_num in track_nums:
                            note_sequences_for_bar.append(note_sequence)
                    self.add_notes(measure_elem, note_sequences_for_bar, staff_num + 1)

                bar_ind += 1

    def add_measure(self, part_spec, part_ind, measure_ind, part_elem, bar,
                    is_start_of_episode, episode_num, episode_title):
        measure_attributes = {"number": f"{measure_ind}"}
        measure_elem = XMLUtils.add_child(self.doc, part_elem, "measure", measure_attributes)
        attributes_elem = XMLUtils.add_child(self.doc, measure_elem, "attributes")
        if measure_ind == 1:
            time_elem = XMLUtils.add_child(self.doc, attributes_elem, "time")
            XMLUtils.add_child(self.doc, time_elem, "beats", {}, "4")
            XMLUtils.add_child(self.doc, time_elem, "beat-type", {}, "4")
            clefs = [clef for (clef, _) in part_spec.clef_track_list]
            XMLUtils.add_child(self.doc, attributes_elem, "staves", {}, f"{len(clefs)}")
            for ind, clef in enumerate(clefs):
                clef_type = "F" if clef == "bass" else "G"
                clef_line = "4" if clef == "bass" else "2"
                clef_elem = XMLUtils.add_child(self.doc, attributes_elem, "clef", {"number": f"{ind + 1}"})
                XMLUtils.add_child(self.doc, clef_elem, "sign", {}, clef_type)
                XMLUtils.add_child(self.doc, clef_elem, "line", {}, clef_line)

        attributes_elem = XMLUtils.add_child(self.doc, measure_elem, "attributes")
        XMLUtils.add_child(self.doc, attributes_elem, "divisions", {}, "128")
        if part_ind == 0 and is_start_of_episode:
            XMLUtils.add_child(self.doc, measure_elem, "bookmark", {"id": f"{episode_num + 1}"})
            direction_elem = XMLUtils.add_child(self.doc, measure_elem, "direction", {"placement": "above"})
            direction_type_elem = XMLUtils.add_child(self.doc, direction_elem, "direction-type")
            ep_title = f"Episode {episode_num + 1}" if episode_title is None else episode_title
            rehearsal_attrs = {"font-size": "8"}
            if self.score_gen_spec.is_lead_sheet:
                start_s = bar.start_tick/960
                ep_title += f" @ {start_s: .1f}s"
            XMLUtils.add_child(self.doc, direction_type_elem, "rehearsal", rehearsal_attrs, ep_title)

        if self.score_gen_spec.show_bar_tag and part_ind == 0 and bar.score_tag is not None:
            direction_elem = XMLUtils.add_child(self.doc, measure_elem, "direction", {"placement": "above"})
            direction_type_elem = XMLUtils.add_child(self.doc, direction_elem, "direction-type")
            XMLUtils.add_child(self.doc, direction_type_elem, "words", {"xml_space": "Yes"}, bar.score_tag)

        if bar.directions is not None:
            dynamics_direction_elem = XMLUtils.add_child(self.doc, measure_elem, "direction", {"placement": "below"})
            direction_type_elem = XMLUtils.add_child(self.doc, dynamics_direction_elem, "direction-type")
            dynamics_elem = XMLUtils.add_child(self.doc, direction_type_elem, "dynamics", {"halign": "left"})
            XMLUtils.add_child(self.doc, dynamics_elem, bar.directions)

        return measure_elem

    def add_notes(self, measure_elem, note_sequences, staff_num):
        denominator = 128
        starting_notes = []
        has_notes = [False for x in range(0, denominator)]
        is_in_rest = False
        for numerator in range(0, denominator):
            notes_for_beat = []
            for note_sequence in note_sequences:
                for note in note_sequence.notes:
                    if note.start_frac == numerator:
                        if note.pitch is not None:
                            notes_for_beat.append(note)
                            for n in range(numerator, numerator + note.num_fracs):
                                has_notes[n] = True
            starting_notes.append(notes_for_beat)

        for numerator in range(1, denominator + 1):
            notes_for_beat = starting_notes[numerator - 1]
            if len(notes_for_beat) > 0:
                is_in_rest = False
                add_chord_annotation = False
                for note in notes_for_beat:
                    self.add_note(measure_elem, note, staff_num, add_chord_annotation)
                    add_chord_annotation = True
            elif not has_notes[numerator - 1] and not is_in_rest:
                n = numerator + 1
                num_fracs = 1
                while n-1 < len(has_notes) and not has_notes[n - 1]:
                    num_fracs += 1
                    n += 1
                self.add_rest(measure_elem, num_fracs, staff_num)
                is_in_rest = True

    def add_rest(self, measure_elem, num_fracs, staff_num):
        breakdown = RhythmUtils.get_note_quantization_split(num_fracs)
        for (b_fracs, num_dots) in breakdown:
            note_elem = XMLUtils.add_child(self.doc, measure_elem, "note")
            XMLUtils.add_child(self.doc, note_elem, "rest")
            XMLUtils.add_child(self.doc, note_elem, "duration", {}, f"{b_fracs}")
            rest_type = self.note_types_hash[b_fracs]
            XMLUtils.add_child(self.doc, note_elem, "type", {}, rest_type)
            XMLUtils.add_child(self.doc, note_elem, "staff", {}, f"{staff_num}")

    def add_note(self, measure_elem, note, staff_num, add_chord_annotation):
        if note.score_chord_name is not None:
            harmony_elem = XMLUtils.add_child(self.doc, measure_elem, "harmony", {"color":"green"})
            root_elem = XMLUtils.add_child(self.doc, harmony_elem, "root")
            XMLUtils.add_child(self.doc, root_elem, "root-step", {}, note.score_chord_name[:note.score_chord_name.index("m")])
            majmin = "major" if "maj" in note.score_chord_name else "minor"
            XMLUtils.add_child(self.doc, harmony_elem, "kind", {"halign":"center"}, majmin)
        note_attributes = {}
        if self.score_gen_spec.show_colours and note.score_colour is not None:
            note_attributes["color"] = note.score_colour
        note_elem = XMLUtils.add_child(self.doc, measure_elem, "note", note_attributes)

        if add_chord_annotation:
            XMLUtils.add_child(self.doc, note_elem, "chord")
        pitch_elem = XMLUtils.add_child(self.doc, note_elem, "pitch")
        pitch_class = ChordUtils.pitch_class(note.pitch)
        octave = ChordUtils.get_octave(note.pitch)
        letter = self.letters[pitch_class]
        XMLUtils.add_child(self.doc, pitch_elem, "step", {}, letter[0])
        XMLUtils.add_child(self.doc, pitch_elem, "octave", {}, f"{octave}")
        if len(letter) == 2:
            XMLUtils.add_child(self.doc, pitch_elem, "alter", {}, "1")

        num_fracs, num_dots = RhythmUtils.get_note_quantization_split(note.num_fracs)[0]
        note_type = self.note_types_hash[num_fracs]
        XMLUtils.add_child(self.doc, note_elem, "type", {}, note_type)
        for i in range(0, num_dots):
            XMLUtils.add_child(self.doc, note_elem, "dot")
        XMLUtils.add_child(self.doc, note_elem, "staff", {}, f"{staff_num}")
        notations_elem = None
        if note.tie_type == "start" or note.tie_type == "mid":
            notations_elem = XMLUtils.add_child(self.doc, note_elem, "notations")
            XMLUtils.add_child(self.doc, notations_elem, "tied", {"type": "start"})
        if note.tie_type == "mid" or note.tie_type == "end":
            if notations_elem is None:
                notations_elem = XMLUtils.add_child(self.doc, note_elem, "notations")
            notations_elem = XMLUtils.add_child(self.doc, note_elem, "notations")
            XMLUtils.add_child(self.doc, notations_elem, "tied", {"type": "stop"})
        if note.cutoff_prop <= 0.5:
            if notations_elem is None:
                notations_elem = XMLUtils.add_child(self.doc, note_elem, "notations")
            articulations_elem = XMLUtils.add_child(self.doc, notations_elem, "articulations")
            XMLUtils.add_child(self.doc, articulations_elem, "staccato")

        XMLUtils.add_child(self.doc, note_elem, "duration", {}, f"{note.num_fracs}")