class FormUtils:

    def merge_episodes(composition, episode_position_lists):
        new_episodes = []
        for ep_list in episode_position_lists:
            new_episodes.append(composition.form.episodes[ep_list[0]])
            for i in range(1, len(ep_list)):
                composition.form.episodes[ep_list[0]].bars.extend(composition.form.episodes[ep_list[i]].bars)
        composition.form.episodes = new_episodes
