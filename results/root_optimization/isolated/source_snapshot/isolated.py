"""Validate the filename and note annotations of one isolated guitar chord."""
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET

PITCH_CLASSES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
STEM = re.compile(r'([1-4])-([EA])([12])-(Major|Minor) (\d{2})')


def load_isolated(path):
    """Return the triad from the first note onset to the last note offset.

    The chord symbol is derived from the documented fingering and shift.
    All annotated pitch classes must equal that triad before it is accepted.
    Leading silence and any unannotated tail remain unlabelled.
    """
    path = Path(path)
    match = STEM.fullmatch(path.stem)
    if not match:
        raise ValueError(f'Unrecognized isolated-chord filename: {path.name}')
    index, shape, position, quality, shift_text = match.groups()
    shift = int(shift_text)
    if shift not in range(11) or (shape, position, quality) != {
        '1': ('E', '1', 'Major'), '2': ('E', '1', 'Minor'),
        '3': ('A', '2', 'Major'), '4': ('A', '2', 'Minor'),
    }[index]:
        raise ValueError(f'Inconsistent fingering or shift: {path.name}')
    root = ({'E': 4, 'A': 9}[shape] + shift) % 12
    quality_code = {'Major': 'maj', 'Minor': 'min'}[quality]
    expected = {(root + interval) % 12 for interval in (0, 4 if quality_code == 'maj' else 3, 7)}
    xml = ET.parse(path).getroot()
    if xml.tag != 'instrumentRecording' or xml.findtext('globalParameter/audioFileName') != path.with_suffix('.wav').name:
        raise ValueError(f'XML audio filename disagrees with path: {path}')
    events = []
    for event in xml.findall('transcription/event'):
        pitch_value = float(event.findtext('pitch'))
        start, end = float(event.findtext('onsetSec')), float(event.findtext('offsetSec'))
        if not math.isfinite(pitch_value) or not pitch_value.is_integer() or not 0 <= pitch_value <= 127:
            raise ValueError(f'Invalid MIDI pitch in {path}')
        if not math.isfinite(start) or not math.isfinite(end) or not 0 <= start < end:
            raise ValueError(f'Invalid note interval in {path}')
        events.append((int(pitch_value), start, end))
    if not events:
        raise ValueError(f'No note events in {path}')
    observed = {p % 12 for p, _, _ in events}
    if observed != expected:
        raise ValueError(f'Filename/XML pitch-class mismatch in {path.name}: {sorted(expected)} != {sorted(observed)}')
    start, end = min(a for _, a, _ in events), max(b for _, _, b in events)
    label = f'{PITCH_CLASSES[root]}:{quality_code}'
    info = dict(group_id=path.stem, fingering=shape, semitone_shift=shift, root_pitch_class=root, quality=quality_code, note_count=len(events), midi_pitches=[p for p, _, _ in events], pitch_classes=sorted(observed), earliest_onset=start, latest_offset=end, recording_date=xml.findtext('globalParameter/recordingDate'))
    return [(start, end, label)], info
