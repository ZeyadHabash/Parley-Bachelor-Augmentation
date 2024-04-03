from dataclasses import dataclass

''' DESIGNER SPECS '''


class ExcerptExpanderDesignSpec:
    def __init__(self, composition_duration_ms=None, num_episodes=None,
                 volume_cycle=None, tempo_cycle=None):
        self.composition_duration_ms = composition_duration_ms
        self.num_episodes = num_episodes
        self.volume_cycle = volume_cycle
        self.tempo_cycle = tempo_cycle


''' GENERATION SPECS '''


class CompositionGenSpec:
    def __init__(self, title=None, seed=None, output_stem=None, form_gen_spec=None, lead_sheet_gen_spec=None,
                     score_gen_spec=None, midi_gen_spec=None):
        self.title = title
        self.seed = seed
        self.output_stem = output_stem
        self.form_gen_spec = form_gen_spec
        self.lead_sheet_gen_spec = lead_sheet_gen_spec
        self.score_gen_spec = score_gen_spec
        self.midi_gen_spec = midi_gen_spec


class ExcerptGenSpec:
    def __init__(self, chord_instrument_types, melody_instrument_types, midi_gen_spec):
        self.chord_instrument_types = chord_instrument_types
        self.melody_instrument_types = melody_instrument_types
        self.midi_gen_spec = midi_gen_spec


class LeadSheetGenSpec:
    def __init__(self):
        pass


class MidiGenSpec:
    def __init__(self, soundfont_class_name=None, soundfont_filepath=None, end_rest_ticks=None):
        self.soundfont_class_name = soundfont_class_name
        self.soundfont_filepath = soundfont_filepath
        self.end_rest_ticks = end_rest_ticks


class FormGenSpec:
    def __init__(self, episode_gen_specs=None):
        self.episode_gen_specs = episode_gen_specs


class EpisodeGenSpec:
    def __init__(self, bar_structure_gen_spec=None, chord_sequence_gen_spec=None, note_sequence_gen_specs=None):
        self.bar_structure_gen_spec = bar_structure_gen_spec
        self.chord_sequence_gen_spec = chord_sequence_gen_spec
        self.note_sequence_gen_specs = note_sequence_gen_specs


class BarStructureGenSpec:
    def __init__(self, episode_target_duration_ms=None,
                 bar_start_target_duration_ms=None,
                 bar_end_target_duration_ms=None,
                 rhythm=None):
        self.episode_target_duration_ms = episode_target_duration_ms
        self.bar_start_target_duration_ms = bar_start_target_duration_ms
        self.bar_end_target_duration_ms = bar_end_target_duration_ms
        self.rhythm = rhythm
        print("Bar Structure: \n", self.episode_target_duration_ms, self.bar_start_target_duration_ms, self.bar_end_target_duration_ms, self.rhythm)


class ChordSequenceGenSpec:
    def __init__(self, override_chord_pitches=None,
                 focal_pitch=None, fixed_key_sig=None, max_repetitions=None):
        self.override_chord_pitches = override_chord_pitches
        self.focal_pitch = focal_pitch
        self.fixed_key_sig = fixed_key_sig
        self.max_repetitions = max_repetitions


class NRTChordSequenceGenSpec(ChordSequenceGenSpec):
    def __init__(self, override_chord_pitches=None,
                 focal_pitch=None, fixed_key_sig=None, max_repetitions=None,
                 start_nro=None, min_cnro_length=None, max_cnro_length=None,
                 is_classic=None, majmin_constraint=None):
        super().__init__(override_chord_pitches, focal_pitch, fixed_key_sig, max_repetitions)
        self.start_nro = start_nro
        self.min_cnro_length = min_cnro_length
        self.max_cnro_length = max_cnro_length
        self.is_classic = is_classic
        self.majmin_constraint = majmin_constraint


class NoteSequenceGenSpec:
    def __init__(self, id=None, track_num=None, channel_num=None, instrument_num=None, volume=None,
                 leads_dynamics_direction=None, octave_offset=None, fixed_key_sig=None):
        self.id = id
        self.track_num = track_num
        self.channel_num = channel_num
        self.instrument_num = instrument_num
        self.volume = volume
        self.leads_dynamics_direction = leads_dynamics_direction
        self.octave_offset = octave_offset
        self.fixed_key_sig = fixed_key_sig


class RhythmGenSpec(NoteSequenceGenSpec):
    def __init__(self, id=None, track_num=None, channel_num=None, instrument_num=None, volume=None,
                 leads_dynamics_direction=None, octave_offset=None, rhythm=None, fixed_key_sig=None):
        super().__init__(id, track_num, channel_num, instrument_num, volume,
                         leads_dynamics_direction, octave_offset, fixed_key_sig)
        self.rhythm = rhythm


class VLMelodyGenSpec(NoteSequenceGenSpec):
    def __init__(self, id=None, track_num=None, channel_num=None, instrument_num=None, volume=None,
                 leads_dynamics_direction=None, octave_offset=None, backbone_length=None, fixed_key_sig=None,
                 note_length=None, passing_notes_policy=None, repetition_policy=None):
        super().__init__(id, track_num, channel_num,instrument_num, volume,
                         leads_dynamics_direction, octave_offset, fixed_key_sig)
        self.backbone_length = backbone_length
        self.note_length = note_length
        self.passing_notes_policy = passing_notes_policy
        self.repetition_policy = repetition_policy


''' EDITING SPECS '''


class RandomEditSpec:
    def __init__(self, track_num=None, change_prop=None, fixed_key_sig=None):
        self.track_num = track_num
        self.change_prop = change_prop
        self.fixed_key_sig = fixed_key_sig

@dataclass
class DiscordanceEditSpec:
    interval_scores: {}
    score_threshold: int
    duration_ticks_threshold: int
    ignore_passing_notes: bool
    tracks_to_edit: []
    edit_technique: ""

class HarmonisationEditSpec:
    def __init__(self, id=None, new_track_num=None, new_channel_num=None,
                 instrument_num=None, track_num_to_harmonise=None,
                 fixed_key_sig=None, note_types_to_change=None, intervals_allowed=None, pitch_range_low=None,
                 pitch_range_high=None, map_to_key_signature=None):
        self.id = id
        self.new_track_num = new_track_num
        self.new_channel_num = new_channel_num
        self.instrument_num = instrument_num
        self.track_num_to_harmonise = track_num_to_harmonise
        self.note_types_to_change = note_types_to_change
        self.fixed_key_sig = fixed_key_sig
        self.intervals_allowed = intervals_allowed
        self.pitch_range_low = pitch_range_low
        self.pitch_range_high = pitch_range_high
        self.map_to_key_signature = map_to_key_signature


class InterestingnessEditSpec:
    def __init__(self, track_num=None, lower_target_interestingness=None, upper_target_interestingness=None,
                 fixed_key_sig=None, bar_types_to_change=None, note_types_to_change=None,
                 pitch_change_choice=None, focal_pitch=None,
                 repetition_policy=None, chord_notes_fixed=None):
        self.track_num = track_num
        self.lower_target_interestingness = lower_target_interestingness
        self.upper_target_interestingness = upper_target_interestingness
        self.fixed_key_sig = fixed_key_sig
        self.bar_types_to_change = bar_types_to_change
        self.note_types_to_change = note_types_to_change
        self.pitch_change_choice = pitch_change_choice
        self.focal_pitch = focal_pitch
        self.repetition_policy = repetition_policy
        self.chord_notes_fixed = chord_notes_fixed


class RepeatedNoteRemovalEditSpec:
    def __init__(self, ordered_track_nums=None):
        self.ordered_track_nums = ordered_track_nums


class RhythmRepetitionEditSpec:
    def __init__(self, rhythm_track_num=None, max_num_repetitions=None,
                 min_num_notes_in_rhythm=None, num_bars_in_window=None):
        self.rhythm_track_num = rhythm_track_num
        self.max_num_repetitions = max_num_repetitions
        self.min_num_notes_in_rhythm = min_num_notes_in_rhythm
        self.num_bars_in_window = num_bars_in_window


''' SCORE GENERATION SPECS '''


class ScorePartGenSpec:
    def __init__(self, part_id, part_name, clef_track_list):
        self.part_id = part_id
        self.part_name = part_name
        self.clef_track_list = clef_track_list


class ScoreGenSpec:
    def __init__(self, composition_title=None, part_gen_specs=None, show_colours=None,
                 show_bar_tag=None, is_lead_sheet=None):
        self.composition_title = composition_title
        self.part_gen_specs = part_gen_specs
        self.show_colours = show_colours
        self.show_bar_tag = show_bar_tag
        self.is_lead_sheet = is_lead_sheet

''' ANALYSIS SPECS '''


class InterestingnessEditAnalyserSpec:
    def __init__(self, track_num=None, min_num_notes=None, num_highlight_passages=None, make_notes_purple=None):
        self.track_num = track_num
        self.min_num_notes = min_num_notes
        self.num_highlight_passages = num_highlight_passages
        self.make_notes_purple = make_notes_purple


class BalanceAnalyserSpec:
    def __init__(self):
        pass

''' MEDIA SPECS '''

class VideoGenSpec:
    def __init__(self, dpi, fps, line_start_bar_indent_pc):
        self.dpi = dpi
        self.fps = fps
        self.line_start_bar_indent_pc = line_start_bar_indent_pc