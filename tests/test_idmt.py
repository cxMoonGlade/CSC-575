import pytest
from chordrec.idmt import convert_chord, load_chords
from chordrec.data import reduce_label


def test_unsupported_and_malformed_symbols_are_not_silently_corrected():
    for symbol in ('D/7Gb', 'GB5', 'Db79', 'Bmin75b', 'Dsus9'):
        assert convert_chord(symbol) == 'X'
    assert convert_chord('NC') == 'N'
    assert reduce_label(convert_chord('Bbmin7/F')) == 'A#:min'
    assert reduce_label(convert_chord('E13/Db')) == 'E:maj'
    assert reduce_label(convert_chord('G5/D')) is None
    assert reduce_label(convert_chord('Fdim/B')) is None


def test_beat_intervals_exclude_prefix_tail_and_metadata(tmp_path):
    path = tmp_path / 'chords.csv'
    path.write_text('8,1.1:C\n9,1.2\n10,1.3:D/7Gb\n11,1.4\n12,2.1:NC\n13,2.2\n1,1\n2,2\n4,4\n')
    intervals, symbols = load_chords(path)
    assert intervals == [(8,9,'C:maj'), (9,10,'C:maj'), (10,11,'X'), (11,12,'X'), (12,13,'N')]
    assert symbols == [('C','C:maj'), ('D/7Gb','X'), ('NC','N')]


def test_nonincreasing_beat_times_fail(tmp_path):
    path = tmp_path / 'bad.csv'
    path.write_text('8,1.1:C\n8,1.2\n1,1\n1,2\n4,4\n')
    with pytest.raises(ValueError, match='increase'):
        load_chords(path)
