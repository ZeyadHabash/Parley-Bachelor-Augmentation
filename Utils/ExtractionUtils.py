class ExtractionUtils:

    def get_all_bars(composition):
        bars = []
        for episode in composition.form.episodes:
            bars.extend(episode.bars)
        return bars

    def get_all_notes(composition):
        all_notes = []
        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    for note in note_sequence.notes:
                        all_notes.append(note)
        return all_notes

    def get_note_sequences_hash(composition):
        note_sequences_hash = {}
        for track_num in ExtractionUtils.get_track_nums(composition):
            note_sequences_hash[track_num] = []
            for episode in composition.form.episodes:
                for bar in episode.bars:
                    for note_sequence in bar.note_sequences:
                        if note_sequence.track_num == track_num:
                            note_sequences_hash[track_num].append(note_sequence)
        return note_sequences_hash

    def get_episode_notes(composition, episode):
        all_notes = []
        for bar in episode.bars:
            for note_sequence in bar.note_sequences:
                for note in note_sequence.notes:
                    all_notes.append(note)
        return all_notes

    def get_track_nums(composition):
        track_nums = []
        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num not in track_nums:
                        track_nums.append(note_sequence.track_num)
        track_nums.sort()
        return track_nums

    def get_track_notes_for_composition(composition):
        track_notes_hash_for_composition = {}
        for track_num in ExtractionUtils.get_track_nums(composition):
            notes = []
            for episode in composition.form.episodes:
                for bar in episode.bars:
                    for note_sequence in bar.note_sequences:
                        if note_sequence.track_num == track_num:
                            for note in note_sequence.notes:
                                notes.append(note)
            track_notes_hash_for_composition[track_num] = notes
        return track_notes_hash_for_composition

    def get_track_notes_for_episode(composition, episode):
        track_notes_hash_for_episode = {}
        for track_num in ExtractionUtils.get_track_nums(composition):
            notes = []
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num == track_num:
                        for note in note_sequence.notes:
                            notes.append(note)
            track_notes_hash_for_episode[track_num] = notes
        return track_notes_hash_for_episode

    def get_bar_notes_for_track(composition, track_num):
        bars = []
        for episode in composition.form.episodes:
            for bar in episode.bars:
                bar_notes = []
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num == track_num:
                        for note in note_sequence.notes:
                            bar_notes.append(note)
                bars.append(bar_notes)
        return bars

    def get_overlapping_note_sets(composition):
        start_ticks_hash = {}
        for ep in composition.form.episodes:
            for bar in ep.bars:
                for note_sequence in bar.note_sequences:
                    for note in note_sequence.notes:
                        if note.pitch is not None and (note.tie_type is None or note.tie_type == "start"):
                            if note.start_tick in start_ticks_hash:
                                start_ticks_hash[note.start_tick].append(note)
                            else:
                                start_ticks_hash[note.start_tick] = [note]
        overlapping_note_sets = []
        start_ticks = list(start_ticks_hash.keys())
        start_ticks.sort()
        for start_tick in start_ticks:
            notes = start_ticks_hash[start_tick]
            if len(overlapping_note_sets) > 0:
                _, prev_set = overlapping_note_sets[-1]
                for note in prev_set:
                    if note.start_tick + note.duration_ticks > start_tick + 5:
                        notes.append(note)
            overlapping_note_sets.append((start_tick, notes))
        return overlapping_note_sets