import pandas as pd
import json
from pathlib import Path

ANNOTATION_CSV = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'data' / 'annotations' / 'annotation_sheet.csv')
OUT_JSON       = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'data' / 'annotations' / 'labelstudio_import.json')
DOCUMENT_ROOT  = '/Users/carolineswartz'

df = pd.read_csv(ANNOTATION_CSV)
tasks = []

for _, row in df.iterrows():
    # Convert absolute path to Label Studio local file URL
    audio_abs = row['audio_path']
    if audio_abs and str(audio_abs) != 'nan':
        rel_path = str(audio_abs).replace(DOCUMENT_ROOT + '/', '')
        audio_url = f'/data/local-files/?d={rel_path}'
    else:
        audio_url = ''

    tasks.append({
        'data': {
            'audio':        audio_url,
            'candidate_id': row['candidate_id'],
            'target_phrase': row['target_phrase'],
            'show_name':    row['show_name'],
            'episode_id':   row['episode_id'],
            'seg_start':    row['seg_start'],
            'seg_end':      row['seg_end'],
            'segment_text': row['segment_text'],
            'prev_text':    str(row['prev_text']),
            'next_text':    str(row['next_text']),
        }
    })

with open(OUT_JSON, 'w') as f:
    json.dump(tasks, f, indent=2)

print(f'Exported {len(tasks)} tasks to {OUT_JSON}')
