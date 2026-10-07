r"""\partCombine in the MusicXML export."""
import pytest

from .musicxml_helpers import convert, measure_lengths, measures, notes, parts, pitch, pitches, validate


@pytest.mark.parametrize('command', [r'\partCombine', r'\partcombine'])
def test_part_combine_two_voices(command):
    root = convert(r"\new Staff %s { c''4 d'' e'' f'' } { a'4 b' c'' d'' }" % command)
    assert len(parts(root)) == 1
    assert pitches(root, voice=1) == ['C5', 'D5', 'E5', 'F5']
    assert pitches(root, voice=2) == ['A4', 'B4', 'C5', 'D5']
    assert measure_lengths(root) == [4]
    assert root.find('part/measure/backup') is not None
    validate(root)


def test_part_combine_several_measures():
    root = convert(r"\new Staff \partCombine { c''1 d''2 e'' } { a'2 b' c''1 }")
    assert measure_lengths(root) == [4, 4]
    assert pitches(root, voice=1) == ['C5', 'D5', 'E5']
    assert pitches(root, voice=2) == ['A4', 'B4', 'C5']


def test_part_combine_with_variables():
    root = convert(r"""
up = { e''2 f'' }
down = { c''2 d'' }
\score { \new Staff \partCombine \up \down }
""")
    assert pitches(root, voice=1) == ['E5', 'F5']
    assert pitches(root, voice=2) == ['C5', 'D5']


def test_part_combine_followed_by_music():
    root = convert(r"\new Staff { \partCombine { c''1 } { a'1 } d''1 }")
    m = measures(root)
    assert measure_lengths(root) == [4, 4]
    assert [pitch(n) for n in m[1].findall('note')] == ['D5']
    assert m[1].find('backup') is None


def test_part_combine_next_to_other_staff():
    root = convert(r"""\score { <<
  \new Staff \partCombine { c''2 d'' } { a'2 b' }
  \new Staff { \clef bass c1 }
>> }""")
    assert len(parts(root)) == 2
    assert pitches(root, 0, voice=1) == ['C5', 'D5']
    assert pitches(root, 0, voice=2) == ['A4', 'B4']
    assert pitches(root, 1) == ['C3']
    validate(root)


def test_part_combine_relative():
    root = convert(r"\new Staff \partCombine \relative c'' { c4 d e f } \relative c' { a4 b c d }")
    assert pitches(root, voice=1) == ['C5', 'D5', 'E5', 'F5']
    # a is a third below c'
    assert pitches(root, voice=2) == ['A3', 'B3', 'C4', 'D4']


def test_part_combine_with_rests_and_ties():
    root = convert(r"\new Staff \partCombine { c''2~ c''4 r } { r4 a'2. }")
    assert pitches(root, voice=1) == ['C5', 'C5', 'r']
    assert pitches(root, voice=2) == ['r', 'A4']
    assert measure_lengths(root) == [4]
    validate(root)


def test_part_combine_in_piano_staff():
    root = convert(r"""\score { \new PianoStaff <<
  \new Staff \partCombine { e''1 } { c''1 }
  \new Staff { \clef bass c1 }
>> }""")
    assert len(parts(root)) == 1
    n = notes(root)
    assert [(pitch(x), x.findtext('staff')) for x in n] == [
        ('E5', '1'), ('C5', '1'), ('C3', '2')]
    validate(root)
