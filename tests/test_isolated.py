"""Check label derivation and malformed isolated-chord annotations."""
import math
import xml.etree.ElementTree as ET
import pytest
from chordrec.isolated import load_isolated


def fixture(path, pitches, intervals):
    root = ET.Element('instrumentRecording')
    global_info = ET.SubElement(root, 'globalParameter')
    ET.SubElement(global_info, 'audioFileName').text = path.with_suffix('.wav').name
    events = ET.SubElement(root, 'transcription')
    for pitch, (start, end) in zip(pitches, intervals):
        event = ET.SubElement(events, 'event')
        for key, value in [('pitch', pitch), ('onsetSec', start), ('offsetSec', end)]:
            ET.SubElement(event, key).text = str(value)
    ET.ElementTree(root).write(path)


def test_strummed_chord_uses_union_and_filename_shift(tmp_path):
    path = tmp_path / '4-A2-Minor 10.xml'
    fixture(path, [55, 62, 70], [(0.2, 2.4), (0.23, 2.5), (0.27, 2.3)])
    reference, info = load_isolated(path)
    assert reference == [(0.2, 2.5, 'G:min')]
    assert info['root_pitch_class'] == 7


def test_pitch_class_mismatch_cannot_be_silently_relabelled(tmp_path):
    path = tmp_path / '1-E1-Major 00.xml'
    fixture(path, [40, 43, 47], [(0.2, 2.5)] * 3)
    with pytest.raises(ValueError, match='pitch-class mismatch'):
        load_isolated(path)


@pytest.mark.parametrize('start,end', [(math.nan, 2.5), (0.2, math.inf), (2.5, 0.2)])
def test_invalid_note_time_is_rejected(tmp_path, start, end):
    path = tmp_path / '1-E1-Major 00.xml'
    fixture(path, [40, 44, 47], [(start, end)] * 3)
    with pytest.raises(ValueError, match='note interval'):
        load_isolated(path)

