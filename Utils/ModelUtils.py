from Parley.Utils.ExtractionUtils import *


class ModelUtils:

    def get_lead_up_notes_hash(composition, episode, track_num, num_prior_notes, episode_cycle):
        lead_up_notes_hash = {}
        track_notes_in_episode = ExtractionUtils.get_track_notes_for_episode(composition, episode)[track_num]
        for ind, note in enumerate(track_notes_in_episode):
            start_at = max(0, ind - num_prior_notes)
            lup = []
            if episode_cycle and ind < num_prior_notes:
                num_extra = num_prior_notes - ind
                lup = track_notes_in_episode[-num_extra:]
            lup.extend(track_notes_in_episode[start_at:ind])
            lead_up_notes_hash[note] = lup
        return lead_up_notes_hash

    def get_one_bar_lead_up_notes(composition):
        lead_up_notes_hash = {}
        for track_num in ExtractionUtils.get_track_nums(composition):
            bar_notes_for_track = ExtractionUtils.get_bar_notes_for_track(composition, track_num)
            for bar_ind, bar in enumerate(bar_notes_for_track):
                for note_ind, note in enumerate(bar):
                    lead_up_notes = []
                    if bar_ind > 0:
                        lead_up_notes.extend(bar_notes_for_track[bar_ind - 1])
                    for i in range(0, note_ind):
                        lead_up_notes.append(bar[i])
                    lead_up_notes_hash[note] = lead_up_notes
        return lead_up_notes_hash
