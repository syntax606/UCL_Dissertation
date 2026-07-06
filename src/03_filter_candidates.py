import pandas as pd
from pathlib import Path

IN_CSV  = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'candidate_targets.csv')
OUT_CSV = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'candidate_targets_filtered.csv')

df = pd.read_csv(IN_CSV)
print(f'Before filter: {len(df):,}')

df['duration'] = df['seg_end'] - df['seg_start']

df = df[df['avg_logprob'] > -0.5]
print(f'After logprob filter:      {len(df):,}')

df = df[df['no_speech_prob'] < 0.3]
print(f'After no_speech filter:    {len(df):,}')

df = df[df['duration'] >= 1.0]
print(f'After min duration filter: {len(df):,}')

df = df[df['duration'] <= 20.0]
print(f'After max duration filter: {len(df):,}')

print()
print('Candidates per phrase after filtering:')
print(df['target_phrase'].value_counts().to_string())

df.to_csv(OUT_CSV, index=False)
print(f'\nSaved to: {OUT_CSV}')
