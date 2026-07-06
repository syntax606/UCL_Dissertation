import subprocess, json, re
import pandas as pd
from pathlib import Path

ANNOTATION_CSV  = str(Path.home() / 'Desktop' / 'pragmatic_contrast' / 'data' / 'annotations' / 'annotation_sheet.csv')
AUDIO_DIR       = Path('/Volumes/Caro Drive/podcast-dissertation-audio/audio copy')
TRANSCRIPTS_DIR = Path('/Volumes/Caro Drive/podcast-dissertation-audio/podcast_transcripts')
CLIPS_DIR       = Path.home() / 'Desktop' / 'pragmatic_contrast' / 'data' / 'clips'
TEST_N          = None  # set to None for full extraction

# Half-windows in seconds (equal time each side of the target word midpoint)
W1_HALF = 3.0   # 6s total
W2_HALF = 5.0   # 10s total
W3_HALF = 8.0   # 16s total

# Map underscored phrase back to the spoken word for matching
PHRASE_WORD = {
    'come_on': 'come',  # match first word of "come on"
}

def find_audio(show_name, episode_id):
    p = AUDIO_DIR / show_name / (episode_id + '.mp3')
    return str(p) if p.exists() else None

def clean(w):
    return re.sub(r'[^a-z]', '', w.lower())

def find_target_midpoint(show_name, episode_id, seg_start, target_phrase):
    """Find the target word in the segment's word list, return its midpoint time."""
    json_path = TRANSCRIPTS_DIR / show_name / (episode_id + '.json')
    target = PHRASE_WORD.get(target_phrase, target_phrase)
    try:
        segs = json.load(open(json_path))['segments']
    except Exception:
        return None
    # locate the segment by start time
    seg = next((s for s in segs if abs(s['start'] - seg_start) < 0.1), None)
    if not seg or 'words' not in seg:
        return None
    for w in seg['words']:
        if clean(w['word']) == target:
            return (w['start'] + w['end']) / 2.0
    return None

def extract_clip(audio_path, center, half, out_path):
    start = max(0.0, center - half)
    duration = half * 2
    cmd = ['ffmpeg', '-y', '-loglevel', 'error',
           '-ss', str(start), '-i', audio_path, '-t', str(duration),
           '-ac', '1', '-ar', '16000', '-af', 'loudnorm', str(out_path)]
    return subprocess.run(cmd, capture_output=True).returncode == 0

df = pd.read_csv(ANNOTATION_CSV)
if TEST_N:
    df = df.head(TEST_N)
    print(f'TEST MODE: first {TEST_N}')

total = len(df)
ok = no_audio = no_word = failed = 0
audio_paths = []

for idx, row in df.iterrows():
    episode_id = row['episode_id']; show_name = row['show_name']
    seg_start = float(row['seg_start']); phrase = row['target_phrase']
    cid = row['candidate_id']

    audio_path = find_audio(show_name, episode_id)
    if not audio_path:
        no_audio += 1; audio_paths.append(''); print(f'  NO AUDIO: {episode_id}'); continue

    center = find_target_midpoint(show_name, episode_id, seg_start, phrase)
    if center is None:
        no_word += 1; audio_paths.append(''); print(f'  NO WORD MATCH: {phrase} in {episode_id[:40]}'); continue

    w1 = CLIPS_DIR / 'W1_local'    / (cid + '.wav')
    w2 = CLIPS_DIR / 'W2_segment'  / (cid + '.wav')
    w3 = CLIPS_DIR / 'W3_discourse'/ (cid + '.wav')

    r1 = extract_clip(audio_path, center, W1_HALF, w1)
    r2 = extract_clip(audio_path, center, W2_HALF, w2)
    r3 = extract_clip(audio_path, center, W3_HALF, w3)

    if r1 and r2 and r3:
        ok += 1; audio_paths.append(str(w1))
        print(f'  [{ok:>4}/{total}] OK  {phrase:8s} {show_name[:20]} center={center:.1f}s')
    else:
        failed += 1; audio_paths.append(''); print(f'  FAILED: {cid}')

full = pd.read_csv(ANNOTATION_CSV)
full['audio_path'] = full['audio_path'].astype(object)
if TEST_N:
    full.loc[:TEST_N-1, 'audio_path'] = audio_paths
else:
    full['audio_path'] = audio_paths
full.to_csv(ANNOTATION_CSV, index=False)

print(f'\nDone. OK: {ok} | No audio: {no_audio} | No word match: {no_word} | Failed: {failed}')
