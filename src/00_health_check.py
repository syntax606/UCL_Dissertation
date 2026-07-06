import json
from pathlib import Path

TRANSCRIPTS_DIR = Path.home() / 'Desktop' / 'podcast_transcripts'

files = list(TRANSCRIPTS_DIR.rglob('*.json'))
print(f'Found {len(files)} JSON files')

bad = []
missing_segments = []

for path in files:
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        if 'segments' not in data:
            missing_segments.append(path.name)
    except Exception as e:
        bad.append((path.name, str(e)))

print(f'  Malformed JSON:       {len(bad)}')
print(f'  Missing segments key: {len(missing_segments)}')

if bad:
    print('\nMalformed files (first 10):')
    for name, err in bad[:10]:
        print(f'  {name}: {err}')
