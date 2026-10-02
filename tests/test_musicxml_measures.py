"""Division of the music into measures in the MusicXML export."""
from fractions import Fraction

import pytest

from .musicxml_helpers import convert, measure_lengths, measures, notes, pitch, pitches, quarters, validate

xfail = pytest.mark.xfail(strict=True, reason="measures are not computed from absolute positions")


def test_time_change():
    root = convert(r"{ \time 3/4 c'2. \time 2/4 c'2 | c'2 }")
    assert measure_lengths(root) == [3, 2, 2]


def test_grace_notes_take_no_time():
    root = convert(r"{ \grace d'16 c'1 c'1 }")
    assert measure_lengths(root) == [4, 4]


@xfail
def test_tuplets():
    root = convert(r"{ \time 2/4 \tuplet 3/2 { c'4 c' c' } c'2 }")
    assert measure_lengths(root) == [2, 2]


@xfail
def test_note_across_barline_is_split_and_tied():
    root = convert(r"{ \time 3/4 c'2 c'2 c'2 }")
    assert measure_lengths(root) == [3, 3]
    q = quarters(root)
    n = notes(root)
    assert [q(x.findtext('duration')) for x in n] == [2, 1, 1, 2]
    assert [[t.get('type') for t in x.findall('tie')] for x in n] == [[], ['start'], ['stop'], []]
    assert [[t.get('type') for t in x.findall('notations/tied')] for x in n] == [[], ['start'], ['stop'], []]
    validate(root)


@xfail
def test_rest_across_barline_is_split():
    root = convert(r"{ \time 3/4 c'2 r2 c'2 }")
    assert measure_lengths(root) == [3, 3]
    assert pitches(root) == ['C4', 'r', 'r', 'C4']


@xfail
def test_partial():
    root = convert(r"{ \partial 4 c'4 | c'1 | c'1 }")
    assert measure_lengths(root) == [1, 4, 4]
    m = measures(root)
    assert m[0].get('implicit') == 'yes'
    assert [x.get('number') for x in m] == ['0', '1', '2']
    validate(root)


@xfail
def test_voices_of_different_rhythm():
    root = convert(r"{ << { c''1 c''1 } \\ { c'2 c'2 c'1 } >> }")
    assert measure_lengths(root) == [4, 4]
    validate(root)


@xfail
def test_voices_after_time_change():
    root = convert(r"{ \time 3/4 c'2. << { e''2. e''2. } \\ { c'4 c'2 c'2. } >> }")
    assert measure_lengths(root) == [3, 3, 3]


def test_time_change_in_the_middle_of_a_voice_section():
    root = convert(r"""\score { <<
  \new Staff { c'1 \time 3/4 c'2. c'2. }
  \new Staff { c'1 c'2. c'2. }
>> }""")
    assert measure_lengths(root, 0) == [4, 3, 3]
    assert measure_lengths(root, 1) == [4, 3, 3]


@xfail
def test_failing_bar_check_is_reported(capsys):
    convert(r"{ c'2 | c'2 }")
    assert 'bar check' in capsys.readouterr().out.lower()


def test_passing_bar_check_is_silent(capsys):
    convert(r"{ c'2 c'2 | c'1 }")
    assert 'bar check' not in capsys.readouterr().out.lower()


def ties(root, part=0):
    return [[t.get('type') for t in n.findall('tie')] for n in notes(root, part)]


@xfail
def test_compound_time_split():
    root = convert(r"{ \time 6/8 c'4. c'2. c'4. }")
    assert measure_lengths(root) == [3, 3]
    q = quarters(root)
    assert [q(n.findtext('duration')) for n in notes(root)] == [
        Fraction(3, 2), Fraction(3, 2), Fraction(3, 2), Fraction(3, 2)]
    assert [n.findtext('type') for n in notes(root)] == ['quarter'] * 4
    assert ties(root) == [[], ['start'], ['stop'], []]
    validate(root)


@xfail
def test_note_over_three_measures():
    root = convert(r"{ \time 2/4 c'1. }")
    assert measure_lengths(root) == [2, 2, 2]
    assert ties(root) == [['start'], ['stop', 'start'], ['stop']]
    validate(root)


@xfail
def test_chord_across_barline():
    root = convert(r"{ \time 3/4 c'2 <c' e'>2 c'2 }")
    assert measure_lengths(root) == [3, 3]
    assert pitches(root) == ['C4', 'C4', 'E4', 'C4', 'E4', 'C4']
    assert ties(root) == [[], ['start'], ['start'], ['stop'], ['stop'], []]
    validate(root)


@xfail
def test_tie_into_split_note():
    root = convert(r"{ \time 3/4 c'2 c'2~ c'2 }")
    assert measure_lengths(root) == [3, 3]
    assert ties(root) == [[], ['start'], ['stop', 'start'], ['stop']]


@xfail
def test_partial_in_three_four():
    root = convert(r"{ \time 3/4 \partial 4 c'4 | c'2. | c'2. }")
    assert measure_lengths(root) == [1, 3, 3]
    assert measures(root)[0].get('implicit') == 'yes'


@xfail
def test_partial_eighth():
    root = convert(r"{ \partial 8 g'8 | c''4 d'' e'' f'' | g''1 }")
    assert measure_lengths(root) == [Fraction(1, 2), 4, 4]


@xfail
def test_multi_measure_rests():
    root = convert(r"{ \time 3/4 R2.*2 | c'2. }")
    assert measure_lengths(root) == [3, 3, 3]


@xfail
def test_skip_across_barline():
    root = convert(r"{ s1. c'2 }")
    assert measure_lengths(root) == [4, 4]
    assert pitches(root) == ['C4']


def test_time_change_in_first_staff_applies_to_all():
    root = convert(r"""\score { <<
  \new Staff { \time 3/4 c'2. c'2. }
  \new Staff { c'2. c'2. }
>> }""")
    assert measure_lengths(root, 0) == [3, 3]
    assert measure_lengths(root, 1) == [3, 3]


@xfail
def test_staff_ending_in_the_middle_of_a_measure():
    root = convert(r"""\score { <<
  \new Staff { c'2. }
  \new Staff { c'2 d'2 e'1 }
>> }""")
    assert measure_lengths(root, 1) == [4, 4]


def test_grace_notes_at_barline():
    root = convert(r"{ \time 2/4 c'2 \grace { d'16 e' } f'2 }")
    assert measure_lengths(root) == [2, 2]
    assert [pitch(n) for n in measures(root)[1].findall('note')] == ['D4', 'E4', 'F4']


@xfail
def test_triplets_across_barline_in_three_four():
    root = convert(r"{ \time 3/4 c'2 \tuplet 3/2 { c'4 c' c' } c'2 }")
    assert measure_lengths(root) == [3, 3]


@xfail
def test_voices_with_tuplets():
    root = convert(r"\new Staff << { \tuplet 3/2 { c''4 c'' c'' } c''2 } \\ { c'1 } >>")
    assert measure_lengths(root) == [4]
    validate(root)


def test_passing_bar_checks_after_time_change(capsys):
    convert(r"{ \time 3/4 c'2. | \time 2/4 c'2 | c'4 c' | }")
    assert 'bar check' not in capsys.readouterr().out.lower()
