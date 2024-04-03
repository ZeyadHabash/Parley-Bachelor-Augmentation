class Composition:

    def __init__(self, title=None, form=None):
        self.title = title
        self.form = form


class Form:

    def __init__(self, episodes=None, number_of_bars=None):
        self.episodes = episodes
        self.number_of_bars = number_of_bars


class Episode:

    def __init__(self, title=None, bars=None, interestingness_profile=None, score_notes=[]):
        self.title = title
        self.bars = bars
        self.interestingness_profile = interestingness_profile
        self.score_notes = score_notes


class Bar:

    def __init__(self, comp_bar_num=None, ep_bar_num=None, start_tick=None,
                 duration_ticks=None, rhythm=None, chords=None, note_sequences=None,
                 track_divisions_hash=None, interestingness_profile=None, score_tag=None,
                 num_bars_to_comp_end=None, num_bars_to_ep_end=None, directions=None,
                 score_notes=[]):
        self.comp_bar_num = comp_bar_num
        self.ep_bar_num = ep_bar_num
        self.start_tick = start_tick
        self.duration_ticks = duration_ticks
        self.rhythm = rhythm
        self.chords = chords
        self.note_sequences = note_sequences
        self.track_divisions_hash = track_divisions_hash
        self.interestingness_profile = interestingness_profile
        self.score_tag = score_tag
        self.num_bars_to_comp_end = num_bars_to_comp_end
        self.num_bars_to_ep_end = num_bars_to_ep_end
        self.directions = directions
        self.score_notes = score_notes


class Chord:

    def __init__(self, chord_name=None, frac=None, num_fracs=None, pitches=None, duration_ticks=None, parent_bar=None):
        self.chord_name = chord_name
        self.frac = frac
        self.num_fracs = num_fracs
        self.pitches = pitches
        self.duration_ticks = duration_ticks
        self.parent_bar = parent_bar


class NRTChordEvent:

    def __init__(self, start_ms=None, event_type=None):
        self.start_ms = start_ms
        self.event_type = event_type


class NoteSequence:

    def __init__(self, id=None, track_num=None, channel_num=None, instrument_num=None, notes=None,
                 interestingness_profile=None, parent_bar=None):
        self.id = id
        self.track_num = track_num
        self.channel_num = channel_num
        self.instrument_num = instrument_num
        self.notes = notes
        self.interestingness_profile = interestingness_profile
        self.parent_bar = parent_bar


class Note:

    def __init__(self, pitch=None, volume=None, start_tick=None, duration_ticks=None, cutoff_prop=None, tied_duration_ticks=None,
                 parent_chord=None, parent_bar=None, parent_note_sequence=None, tie_type=None,
                 is_backbone_note=None, is_backbone_starter=None, start_frac=None, num_fracs=None,
                 score_colour=None, interestingness_profile=None, edit_improvement=None, edit_index=None,
                 score_chord_name=None, score_notes=[]):
        self.pitch = pitch
        self.volume = volume
        self.start_tick = start_tick
        self.duration_ticks = duration_ticks
        self.cutoff_prop = cutoff_prop
        self.tied_duration_ticks = tied_duration_ticks
        self.parent_chord = parent_chord
        self.parent_bar = parent_bar
        self.parent_note_sequence = parent_note_sequence
        self.tie_type = tie_type
        self.is_backbone_note = is_backbone_note
        self.is_backbone_starter = is_backbone_starter
        self.start_frac = start_frac
        self.num_fracs = num_fracs
        self.score_colour = score_colour
        self.interestingness_profile = interestingness_profile
        self.edit_improvement = edit_improvement
        self.edit_index = edit_index
        self.score_chord_name = score_chord_name
        self.score_notes = score_notes

    def __copy__(self):
        interestingness_profile = None if self.interestingness_profile == None else self.interestingness_profile.copy()
        c = Note(self.pitch, self.volume, self.start_tick, self.duration_ticks, self.cutoff_prop, self.tied_duration_ticks,
                 self.parent_chord, self.parent_bar, self.parent_note_sequence, self.tie_type, self. is_backbone_note,
                 self.is_backbone_starter, self.start_frac, self.num_fracs, self.score_colour,
                 interestingness_profile, self.edit_improvement, self.edit_index, self.score_chord_name,
                 self.score_notes)
        return c

class ScoreNote:
    def __init__(self, text=None, colour=None):
        self.text = text
        self.colour = colour