from mido import MidiFile, MidiTrack, Message
import os

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

class MidiGenerator:

    def __init__(self, gen_spec):
        self.gen_spec = gen_spec

    def note_on_message(self, channel, pitch, volume):
        return Message(type='note_on', channel=channel, note=pitch, velocity=clamp(volume, 0, 127), time=0)

    def note_off_message(self, channel, pitch, volume, duration):
        return Message(type='note_off', channel=channel, note=pitch, velocity=clamp(volume, 0, 127), time=duration)

    def add_note(self, track, channel, pitch, volume, duration):
        track.append(self.note_on_message(channel, pitch, clamp(volume, 0, 127)))
        track.append(self.note_off_message(channel, pitch, clamp(volume, 0, 127), duration))

    def add_rest(self, track, channel, duration):
        track.append(self.note_on_message(channel, 60, 0))
        track.append(self.note_off_message(channel, 60, 0, duration))

    def play_pitch_classes(self, midi_filepath, pitch_classes, ticks_per_note):
        midi_file = MidiFile(type=1)
        midi_file.tracks = [MidiTrack()]
        midi_file.tracks[0].append(Message('program_change', channel=0, program=0, time=0))
        for pc in pitch_classes:
            self.add_note(midi_file.tracks[0], 0, pc + 57, 127, ticks_per_note)
        midi_file.save(midi_filepath)
        os.system(f"fluidsynth {self.gen_spec.soundfont_filepath} --quiet --no-shell {midi_filepath}")

    def play_chord_sequence(self, midi_filepath, composition):
        midi_file = MidiFile(type=1)
        midi_file.tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
        for channel, track in enumerate(midi_file.tracks):
            track.append(Message('program_change', channel=channel, program=0, time=0))

        for episode in composition.form.episodes:
            for bar in episode.bars:
                for chord in bar.chords:
                    duration = int(round(chord.duration_ticks))
                    for channel, pitch in enumerate(chord.pitches):
                        track = midi_file.tracks[channel]
                        self.add_note(track, channel, pitch, 127, duration)

        midi_file.save(midi_filepath)
        os.system(f"fluidsynth {self.gen_spec.soundfont_filepath} --quiet --no-shell {midi_filepath}")

    def play_composition(self, midi_filepath, composition):
        self.save_composition(midi_filepath, composition)
        os.system(f"fluidsynth {self.gen_spec.soundfont_filepath} --quiet --no-shell {midi_filepath}")

    def save_composition(self, midi_filepath, composition):
        midi_file = self.get_midi_file(composition)
        midi_file.save(midi_filepath)

    def get_midi_file(self, composition):
        midi_file = MidiFile(type=1)
        tracks_hash = {}
        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num not in tracks_hash:
                        midi_track = MidiTrack()
                        tracks_hash[note_sequence.track_num] = midi_track
                        midi_file.tracks.append(midi_track)
                        midi_track.append(Message('program_change', channel=note_sequence.channel_num,
                                                  program=note_sequence.instrument_num, time=0))

        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    track = tracks_hash[note_sequence.track_num]
                    channel = note_sequence.channel_num
                    for note in note_sequence.notes:
                        if note.tie_type is None or note.tie_type == "start":
                            dticks = note.duration_ticks if note.tied_duration_ticks is None else note.tied_duration_ticks
                            if note.pitch is not None:
                                if note.cutoff_prop == 1:
                                    pitch = note.pitch if note_sequence.channel_num != 9 else note_sequence.instrument_num
                                    self.add_note(track, channel, pitch, note.volume, dticks - 10)
                                    self.add_rest(track, channel, 10)
                                else:
                                    note_ticks = int(round(dticks * note.cutoff_prop))
                                    rest_ticks = dticks - note_ticks
                                    pitch = note.pitch if note_sequence.channel_num != 9 else note_sequence.instrument_num
                                    self.add_note(track, channel, pitch, note.volume, note_ticks - 10)
                                    self.add_rest(track, channel, rest_ticks + 10)
                            else:
                                self.add_rest(track, channel, dticks)
        if self.gen_spec.end_rest_ticks is not None and self.gen_spec.end_rest_ticks > 0:
            self.add_rest(tracks_hash[1], 1, self.gen_spec.end_rest_ticks)
        return midi_file
