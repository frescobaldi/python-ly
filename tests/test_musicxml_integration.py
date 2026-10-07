"""Combinations of features of the MusicXML export."""
from fractions import Fraction

from .musicxml_helpers import (
    convert, divisions, measure_lengths, measures, notes, pitch, pitches,
    quarters, validate)


def test_after_grace_with_fraction_and_articulation():
    root = convert(r"{ \afterGrace 7/8 c'2-> { d'16 } f'2 }")
    n = notes(root)
    assert pitches(root) == ['C4', 'D4', 'F4']
    assert n[0].find('notations/articulations/accent') is not None
    assert n[1].find('grace').get('steal-time-previous') == '12.5'
    assert measure_lengths(root) == [4]
    validate(root)


def test_transposed_chord_names():
    root = convert(r"\transpose c d \chords { c1 f1/a bes1:7 }")
    h = root.findall('.//harmony')
    assert [(x.findtext('root/root-step'), x.findtext('bass/bass-step')) for x in h] == [
        ('D', None), ('G', 'B'), ('C', None)]
    validate(root)


def test_transposed_chordmode_notes():
    root = convert(r"\transpose c d \new Staff \chordmode { c1:7 }")
    assert pitches(root) == ['D3', 'F#3', 'A3', 'C4']


def test_lyrics_on_split_notes():
    root = convert(r"""\score { <<
  \new Voice = "m" { \time 3/4 c'2 d'2 e'2 }
  \new Lyrics \lyricsto "m" { a b c }
>> }""")
    assert [(pitch(n), [l.findtext('text') for l in n.findall('lyric')]) for n in notes(root)] == [
        ('C4', ['a']), ('D4', ['b']), ('D4', []), ('E4', ['c'])]
    validate(root)


def test_chord_name_offset_needs_finer_divisions():
    root = convert(r"""\score { <<
  \chords { c8 g2..:7 }
  \new Staff { c'1 }
>> }""")
    h = root.findall('part/measure/harmony')
    assert len(h) == 2
    assert divisions(root) == 2
    assert h[1].findtext('offset') == '1'
    validate(root)


def test_drum_chord_at_end_of_measure():
    root = convert(r"\new DrumStaff \drummode { <bd hh>2 <sn hh>2 <bd hh>1 }")
    assert measure_lengths(root) == [4, 4]
    assert [len(m.findall('note')) for m in measures(root)] == [4, 2]
    validate(root)


def test_tuplet_with_rest_at_barline():
    root = convert(r"{ \time 2/4 \tuplet 3/2 { c'4 r c' } c'2 }")
    assert measure_lengths(root) == [2, 2]
    assert divisions(root) == 3
    validate(root)


def test_dynamic_on_empty_chord_in_measures():
    root = convert(r"{ c'1 <>\p d'1 }")
    m = measures(root)
    assert measure_lengths(root) == [4, 4]
    assert m[0].find('direction') is None
    assert m[1].find('direction/direction-type/dynamics/p') is not None
    validate(root)


def test_part_combine_across_barlines():
    root = convert(r"\new Staff \partCombine { \time 3/4 c''2. c''2. } { a'2 a'1 }")
    assert measure_lengths(root) == [3, 3]
    q = quarters(root)
    assert [q(n.findtext('duration')) for n in notes(root) if n.findtext('voice') == '2'] == [2, 1, 3]
    validate(root)


def test_repeat_with_chords_and_lyrics():
    root = convert(r"""\score { <<
  \chords { \repeat volta 2 { c1 } g1:7 }
  \new Voice = "m" { \repeat volta 2 { e'1 } d'1 }
  \new Lyrics \lyricsto "m" { la lo }
>> }""")
    m = measures(root)
    assert len(m) == 2
    assert m[0].find("barline[@location='left']/repeat").get('direction') == 'forward'
    assert m[0].find("barline[@location='right']/repeat").get('direction') == 'backward'
    assert [len(x.findall('harmony')) for x in m] == [1, 1]
    assert [[l.findtext('text') for l in n.findall('lyric')] for n in notes(root)] == [['la'], ['lo']]
    validate(root)


def test_after_grace_in_transposed_variable():
    root = convert(r"""
orn = \afterGrace c'2 { d'16 }
\score { \transpose c d { \orn e'2 } }
""")
    assert pitches(root) == ['D4', 'E4', 'F#4']
    assert measure_lengths(root) == [4]


def test_addlyrics_for_voices_in_staff_group():
    root = convert(r"""\score {
  \new StaffGroup <<
    \new Voice = "S" { \set Staff.instrumentName = #"Cantus" c''2 d'' }
    \addlyrics { Du tout }
    \new Voice = "B" { \set Staff.instrumentName = #"Bassus" c2 g, }
    \addlyrics { plon giet }
  >>
}""")
    assert [p.findtext('part-name') for p in root.findall('part-list/score-part')] == [
        'Cantus', 'Bassus']
    assert [[(pitch(n), [l.findtext('text') for l in n.findall('lyric')]) for n in notes(root, i)]
            for i in range(2)] == [
        [('C5', ['Du']), ('D5', ['tout'])],
        [('C3', ['plon']), ('G2', ['giet'])],
    ]
    validate(root)
