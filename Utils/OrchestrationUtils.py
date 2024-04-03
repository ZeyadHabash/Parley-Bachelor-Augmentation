class OrchestrationUtils:

    def replace_instrument_num(composition, track_num, instrument_num):
        for episode in composition.form.episodes:
            for bar in episode.bars:
                for note_sequence in bar.note_sequences:
                    if note_sequence.track_num == track_num:
                        note_sequence.instrument_num = instrument_num
                        