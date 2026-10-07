"""The <divisions> value in the MusicXML export."""
import pytest


from .musicxml_helpers import convert, divisions, notes, validate

xfail = pytest.mark.xfail(strict=True, reason="divisions are not minimal")


def durations(root):
    return [int(n.findtext('duration')) for n in notes(root) if n.find('grace') is None]


def test_quarters():
    root = convert(r"{ c'4 d' e' f' }")
    assert divisions(root) == 1
    assert durations(root) == [1, 1, 1, 1]


def test_binary_durations():
    root = convert(r"{ c'8 c'16 c'32 c'32 c'4 c'2 }")
    assert divisions(root) == 8
    assert durations(root) == [4, 2, 1, 1, 8, 16]


def test_dotted():
    root = convert(r"{ c'4. c'8 c'2 }")
    assert divisions(root) == 2
    assert durations(root) == [3, 1, 4]


def test_triplets():
    root = convert(r"{ \tuplet 3/2 { c'4 c' c' } c'2 }")
    assert divisions(root) == 3
    assert durations(root) == [2, 2, 2, 6]


def test_nested_tuplets():
    root = convert(r"{ \tuplet 3/2 { c'8 \tuplet 3/2 { d'16 e' f' } g'8 } r2. }")
    assert divisions(root) == 9
    assert durations(root) == [3, 1, 1, 1, 3, 27]
    validate(root)


def test_triplet_and_sixteenth():
    root = convert(r"{ \tuplet 3/2 { c'8 c' c' } c'16 c' c'8 c'2 }")
    assert divisions(root) == 12
    assert durations(root) == [4, 4, 4, 3, 3, 6, 24]


def test_quintuplet_and_triplet():
    root = convert(r"{ \tuplet 5/4 { c'16 c' c' c' c' } \tuplet 3/2 { c'8 c' c' } c'2 }")
    assert divisions(root) == 15
    assert durations(root) == [3, 3, 3, 3, 3, 5, 5, 5, 30]


def test_grace_notes_do_not_affect_divisions():
    root = convert(r"{ \grace { c'32 } d'4 e' f' g' }")
    assert divisions(root) == 1


def test_scale_durations():
    root = convert(r"{ \scaleDurations 2/3 { c'4 c' c' } c'2 }")
    assert divisions(root) == 3
    assert durations(root) == [2, 2, 2, 6]


def test_sixty_fourth():
    root = convert(r"{ c'64 c' c' c' c'16 c'8 c'4 c'2 }")
    assert divisions(root) == 16
    assert durations(root) == [1, 1, 1, 1, 4, 8, 16, 32]


def test_dotted_eighth_and_sixteenth():
    root = convert(r"{ c'8. c'16 c'4 c'2 }")
    assert divisions(root) == 4
    assert durations(root) == [3, 1, 4, 8]


def test_rests_in_tuplets():
    root = convert(r"{ \tuplet 3/2 { c'8 r c' } c'4 c'2 }")
    assert divisions(root) == 3
    assert durations(root) == [1, 1, 1, 3, 6]
    validate(root)


def test_divisions_are_the_same_for_all_parts():
    root = convert(r"""\score { <<
  \new Staff { c'4 c' c' c' }
  \new Staff { \tuplet 3/2 { c'4 c' c' } c'2 }
>> }""")
    assert divisions(root, 0) == divisions(root, 1) == 3
    assert durations(root) == [3, 3, 3, 3]
    validate(root)


def test_backup_after_tuplets():
    root = convert(r"\new Staff << { \tuplet 3/2 { c''4 c'' c'' } c''2 } \\ { c'1 } >>")
    assert divisions(root) == 3
    assert [int(b.findtext('duration')) for b in root.iter('backup')] == [12]
    validate(root)


def test_tuplet_in_chord():
    root = convert(r"{ \tuplet 3/2 { <c' e'>4 d' e' } c'2 }")
    assert divisions(root) == 3
    assert durations(root) == [2, 2, 2, 2, 6]


def test_multi_measure_rest_duration():
    root = convert(r"{ R1*2 c'1 }")
    assert divisions(root) == 1
    assert durations(root)[-1] == 4


def test_scale_durations_without_tuplet_bracket():
    root = convert(r"{ \scaleDurations 2/3 { c'4 c' c' } c'2 }")
    assert root.find('.//tuplet') is None


def test_divisions_written_once():
    root = convert(r"{ c'4 d' e' f' | \tuplet 3/2 { c'4 c' c' } c'2 }")
    assert len(root.findall('part/measure/attributes/divisions')) == 1
