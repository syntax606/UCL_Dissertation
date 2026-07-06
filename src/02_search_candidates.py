import duckdb
import pandas as pd
from pathlib import Path

DB_PATH    = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'corpus.duckdb')
OUT_CSV    = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'candidate_targets.csv')
TEST_SHOW  = None  # set to None for full search

TARGETS = {
    'yeah':    r'\byeah\b',
    'right':   r'\bright\b',
    'sure':    r'\bsure\b',
    'okay':    r'\b(okay|ok)\b',
    'great':   r'\bgreat\b',
    'fine':    r'\bfine\b',
    'really':  r'\breally\b',
    'come_on': r'\bcome on\b',
}

conn = duckdb.connect(DB_PATH, read_only=True)
all_rows = []

show_filter = f"AND show_name = '{TEST_SHOW}'" if TEST_SHOW else ''
if TEST_SHOW:
    print(f'TEST MODE: {TEST_SHOW}')
print('-' * 60)

for phrase, pattern in TARGETS.items():
    results = conn.execute(f'''
        SELECT
            episode_id || '_' || CAST(segment_id AS VARCHAR) || '_{phrase}' AS candidate_id,
            '{phrase}'   AS target_phrase,
            episode_id,
            show_name,
            segment_id,
            seg_start,
            seg_end,
            text         AS segment_text,
            prev_text,
            next_text,
            avg_logprob,
            no_speech_prob
        FROM segments
        WHERE regexp_matches(lower(text), '{pattern}')
        {show_filter}
    ''').df()
    print(f'  {phrase:12s}: {len(results):>8,} candidates')
    all_rows.append(results)

df = pd.concat(all_rows, ignore_index=True)

df['audio_path']  = ''
df['status']      = 'unreviewed'
df['label']       = ''
df['confidence']  = ''
df['notes']       = ''

df.to_csv(OUT_CSV, index=False)
print('-' * 60)
print(f'Total candidates: {len(df):,}')
print(f'Saved to: {OUT_CSV}')
conn.close()
