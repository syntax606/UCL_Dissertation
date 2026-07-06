import pandas as pd
from pathlib import Path

IN_CSV  = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'candidate_targets_filtered.csv')
OUT_CSV = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'data' / 'annotations' / 'annotation_sheet.csv')
N_PER_PHRASE = 195
SEED = 42

df = pd.read_csv(IN_CSV)
shows = df['show_name'].nunique()
print(f'{len(df):,} candidates across {shows} shows')

frames = []
for phrase, group in df.groupby('target_phrase'):
    n_shows = group['show_name'].nunique()
    per_show = max(1, N_PER_PHRASE // n_shows)
    parts = []
    for show, sg in group.groupby('show_name'):
        parts.append(sg.sample(min(per_show, len(sg)), random_state=SEED))
    sample = pd.concat(parts)
    if len(sample) < N_PER_PHRASE:
        rest = group[~group.index.isin(sample.index)]
        short = N_PER_PHRASE - len(sample)
        if len(rest) >= short:
            sample = pd.concat([sample, rest.sample(short, random_state=SEED)])
    if len(sample) > N_PER_PHRASE:
        sample = sample.sample(N_PER_PHRASE, random_state=SEED)
    print(f'  {phrase:12s}: {len(sample):>4}')
    frames.append(sample)

final = pd.concat(frames, ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)
cols = ['candidate_id','target_phrase','episode_id','show_name','seg_start','seg_end',
        'duration','segment_text','prev_text','next_text','audio_path','status','label','confidence','notes']
final = final[cols]
final.to_csv(OUT_CSV, index=False)
print(f'\nTotal: {len(final):,}')
