import json, duckdb
from pathlib import Path

TRANSCRIPTS_DIR = Path.home() / 'Desktop' / 'podcast_transcripts'
DB_PATH = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'corpus.duckdb')
TEST_SHOW = None  # set to None for full ingest

conn = duckdb.connect(DB_PATH)
conn.execute('''
    CREATE TABLE IF NOT EXISTS segments (
        episode_id      VARCHAR,
        show_name       VARCHAR,
        segment_id      INTEGER,
        seg_start       DOUBLE,
        seg_end         DOUBLE,
        text            VARCHAR,
        prev_text       VARCHAR,
        next_text       VARCHAR,
        avg_logprob     DOUBLE,
        no_speech_prob  DOUBLE,
        words_json      VARCHAR
    )
''')

done = set(r[0] for r in conn.execute(
    'SELECT DISTINCT episode_id FROM segments').fetchall())

if TEST_SHOW:
    files = list((TRANSCRIPTS_DIR / TEST_SHOW).glob('*.json'))
    print(f'TEST MODE: {TEST_SHOW}')
else:
    files = list(TRANSCRIPTS_DIR.rglob('*.json'))

total_files = len(files)
print(f'Files to process: {total_files} | Already ingested: {len(done)}')
print('-' * 60)

total_rows = 0
skipped = 0

for n, path in enumerate(files, 1):
    episode_id = path.stem
    show_name = path.parent.name

    if episode_id in done:
        skipped += 1
        continue

    try:
        data = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        print(f'  SKIP {path.name}: {e}')
        continue

    segments = data.get('segments', [])
    rows = []
    for i, seg in enumerate(segments):
        rows.append((
            episode_id,
            show_name,
            int(seg['id']),
            float(seg['start']),
            float(seg['end']),
            seg['text'].strip(),
            segments[i-1]['text'].strip() if i > 0 else '',
            segments[i+1]['text'].strip() if i < len(segments)-1 else '',
            seg.get('avg_logprob'),
            seg.get('no_speech_prob'),
            json.dumps(seg.get('words', []))
        ))

    conn.executemany(
        'INSERT INTO segments VALUES (?,?,?,?,?,?,?,?,?,?,?)', rows)
    total_rows += len(rows)

    pct = (n / total_files) * 100
    print(f'  [{n:>4}/{total_files}] {pct:5.1f}%  |  {total_rows:>8,} rows  |  {show_name[:30]}')

conn.execute('CREATE INDEX IF NOT EXISTS idx_episode ON segments (episode_id)')
print('-' * 60)
print(f'Done. Files processed: {n} | Rows ingested: {total_rows:,} | Skipped: {skipped}')
conn.close()
