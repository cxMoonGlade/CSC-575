"""Read beat-wise chord annotations from IDMT-SMT-Guitar subset 4."""
from pathlib import Path
import re

import mir_eval.chord

# The guide does not define the chord vocabulary. Map the conventional
# spellings below; combined suffixes such as 79 remain X.
QUALITIES = {'': 'maj', 'maj': 'maj', 'min': 'min', '7': '7', 'maj7': 'maj7',
             'min7': 'min7', 'dim': 'dim', 'dim7': 'dim7', '5': '5',
             'sus2': 'sus2', 'sus4': 'sus4', '9': '9', 'maj9': 'maj9',
             'min9': 'min9', '11': '11', 'min11': 'min11', '13': '13',
             'maj13': 'maj13', 'min13': 'min13'}
ROOT = re.compile(r'^([A-G](?:#|b)?)(.*)$')
BASS = re.compile(r'^[A-G](?:#|b)?$')
BEAT = re.compile(r'^\d+\.\d+(?::(.*))?$')


def convert_chord(symbol):
    """Map explicit standard symbols to Harte labels; preserve ambiguity as X.

    NC is interpreted as no chord; the dataset guide does not define this
    abbreviation. Inversions do not affect major/minor evaluation, but their
    absolute bass-note syntax must still be valid.
    """
    if symbol == 'NC':
        return 'N'
    parts = symbol.split('/')
    if len(parts) > 2 or (len(parts) == 2 and not BASS.fullmatch(parts[1])):
        return 'X'
    match = ROOT.fullmatch(parts[0])
    if not match or match[2] not in QUALITIES:
        return 'X'
    label = f'{match[1]}:{QUALITIES[match[2]]}'
    try:
        mir_eval.chord.encode(label, reduce_extended_chords=False)
    except mir_eval.chord.InvalidChordException:
        return 'X'
    return label


def load_chords(path):
    """Return intervals between first and last annotated beats, plus symbol pairs.

    The three footer rows describe repetitions and metre. No labels are
    extrapolated into the unannotated control signal or trailing audio.
    """
    lines = Path(path).read_text(encoding='utf-8-sig').splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    if len(lines) < 5:
        raise ValueError('Expected beat events and three metadata rows')
    for footer in lines[-3:]:
        if not re.fullmatch(r'\d+\s*,\s*\d+', footer):
            raise ValueError(f'Invalid footer in {path}: {footer}')
    beats = []
    symbols = []
    current = 'X'
    for line in lines[:-3]:
        parts = line.split(',', 1)
        if len(parts) != 2:
            raise ValueError(f'Invalid beat row: {line}')
        timestamp = float(parts[0])
        match = BEAT.fullmatch(parts[1].strip())
        if not match or not 0 <= timestamp < float('inf'):
            raise ValueError(f'Invalid beat position: {line}')
        if beats and timestamp <= beats[-1][0]:
            raise ValueError(f'Beat times must increase: {path}')
        if match[1] is not None:
            raw = match[1].strip()
            current = convert_chord(raw)
            symbols.append((raw, current))
        beats.append((timestamp, current))
    intervals = [(a[0], b[0], a[1]) for a, b in zip(beats[:-1], beats[1:])]
    return intervals, symbols
