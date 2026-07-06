OFFLINE ANNOTATOR
=================

1. AirDrop / copy the annotator_*.html files to the iPad (save to Files).
2. Open one in Safari. Everything (audio + scheme) is inside the file; no network needed.
3. Label clips. Progress autosaves to Safari's local storage as you go.
4. Tap EXPORT often. It downloads a JSON and copies it to the clipboard;
   AirDrop/email that JSON back to the Mac.
5. On the Mac: python3 src/08_merge_offline_annotations.py <exported>.json [...]

Tip: do not 'Clear History and Website Data' in Safari mid-trip, or unexported
progress is lost. Exporting after each sitting is the safe habit.
