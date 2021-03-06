# author: istewart6 (some help from ssoni)
"""
Code to break subtitle dialogue
into 60 equal-length chunks per episode.
"""
from __future__ import division
import pandas as pd
from datetime import datetime
import re, os

def convert_time(time_):
    new_time = datetime.strptime(time_, '%H:%M:%S,%f')
    new_time = new_time.hour * 60 + new_time.minute + new_time.second / 60
    return new_time

EPISODES=10
SEASONS=6
def main():
    subtitle_dir = '../data/subtitles/subtitlesInTSV/'
    metadata_file = '../vis/data/episode_metadata.csv'
    all_episodes = [f for f in os.listdir(subtitle_dir) 
                    if re.findall('S[0-9]E[0-9]+.tsv', f)]
    sorted_episodes = sorted(all_episodes)
    episode_data = {e : pd.read_csv(os.path.join(subtitle_dir, e), sep='\t') 
                    for e in sorted_episodes}
    episode_metadata = pd.read_csv(metadata_file)
    seasons = ((episode_metadata['No. overall'] - 1) / EPISODES).astype(int) + 1
    print('got seasons %s'%(seasons))
    episodes = (((episode_metadata['No. overall'] - 1) % EPISODES) + 1)    
    print('got episodes %s'%(episodes))
    # get lookup 
    combined_season_episode = ('S' + seasons.astype(str) + 'E' + episodes.astype(str))
    runtime_lookup = dict(zip(combined_season_episode, episode_metadata['Runtime']))
    print('got runtime lookup %s'%(runtime_lookup))
    # chunk_length = 2
    n_chunks = 60
    for e in sorted_episodes:
        e_data = episode_data[e]
        season_episode = re.findall('S[1-6]E[0-9]+', e)[0]
        total = runtime_lookup[season_episode]
        # print('final datum %s'%(e_data.loc[e_data.index[-1]]['endTime']))
        end = e_data['endTime'].max()
        end = convert_time(end)
        total = max(total, end)
        chunk_length = total / n_chunks
        # print('about to convert end time data %s'%(e_data['endTime']))
        chunks = e_data.apply(lambda r : int(convert_time(r['startTime']) / chunk_length), 
                                axis=1)
        e_data['chunk'] = chunks
        fname = os.path.join(subtitle_dir, '%s.tsv'%(season_episode))
        e_data.to_csv(fname, sep='\t', index=False)

if __name__ == '__main__':
    main()
