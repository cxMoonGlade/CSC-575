"""Check annotation coverage and unchanged audio in the diagnostic player."""
import base64
import json
import re
import wave

import pytest

from chordrec.diagnostic_player import coverage_intervals, write_diagnostic_player


def test_coverage_distinguishes_unknown_chords_and_unannotated_audio():
    reference = [(1, 2, 'C:7'), (2, 3, 'N'), (3, 4, 'N'),
                 (4, 5, 'C:sus4'), (6, 7, 'X')]
    assert coverage_intervals(reference, 8) == [
        (0, 1, 'unannotated'), (1, 2, 'chord'), (2, 4, 'N'),
        (4, 5, 'unsupported'), (5, 6, 'unannotated'),
        (6, 7, 'unsupported'), (7, 8, 'unannotated')]


@pytest.mark.parametrize('reference', [[(0, 2, 'N'), (1, 3, 'N')],
                                       [(0, float('nan'), 'N')], [(0, 9, 'N')]])
def test_invalid_annotation_times_fail(reference):
    with pytest.raises(ValueError):
        coverage_intervals(reference, 8)


def test_player_preserves_audio_and_dataset_attribution(tmp_path):
    source = tmp_path / 'source.wav'
    with wave.open(str(source), 'wb') as recording:
        recording.setnchannels(1)
        recording.setsampwidth(2)
        recording.setframerate(8000)
        recording.writeframes(b'\x00\x00' * 8000)
    reference = [(0.2, 0.4, 'N'), (0.4, 0.6, 'N'), (0.6, 0.8, 'C:maj')]
    output = tmp_path / 'player.html'
    write_diagnostic_player(output, source, 'test <title>', reference,
                            {'Saved': [(0, 1, 'C:maj')]}, dataset='idmt')
    page = output.read_text()
    embedded = re.search(r'data:audio/wav;base64,([^\"]+)', page).group(1)
    assert base64.b64decode(embedded) == source.read_bytes()
    assert 'CC BY-NC-ND 4.0' in page and 'GuitarSet' not in page
    assert 'test &lt;title&gt;' in page
    payload = json.loads(re.search(r'<script id="payload" type="application/json">(.*?)</script>', page).group(1))
    assert payload['focus'] == [[0.2, 0.6]]
    assert payload['sourceNC'] is True
    write_diagnostic_player(output, source, 'GuitarSet example', reference,
                            {'Saved': [(0, 1, 'C:maj')]}, dataset='guitarset')
    page = output.read_text()
    assert 'CC BY 4.0' in page and 'CC BY-NC-ND' not in page
    assert 'Source NC is mapped' not in page
