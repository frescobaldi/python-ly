r"""\afterGrace in the MusicXML export."""
import pytest

from .musicxml_helpers import convert, measure_lengths, measures, notes, pitch, pitches, validate

xfail = pytest.mark.xfail(strict=True, reason=r"\afterGrace is not implemented")


def test_after_grace_notes():
    root = convert(r"{ \afterGrace c'2 { d'16 e' } f'2 }")
    n = notes(root)
    assert pitches(root) == ['C4', 'D4', 'E4', 'F4']
    assert [x.find('grace') is not None for x in n] == [False, True, True, False]
    assert [x.findtext('type') for x in n] == ['half', '16th', '16th', 'half']
    assert measure_lengths(root) == [4]
    validate(root)


@xfail
def test_after_grace_steals_time_from_main_note():
    root = convert(r"{ \afterGrace c'2 { d'16 e' } f'2 }")
    graces = [x.find('grace') for x in notes(root) if x.find('grace') is not None]
    # LilyPond's default afterGraceFraction is 3/4
    assert [g.get('steal-time-previous') for g in graces] == ['25', '25']
    assert all(g.get('slash') is None for g in graces)


def test_after_grace_does_not_affect_following_bars():
    root = convert(r"{ \afterGrace c'1 { d'16 } e'1 f'1 }")
    assert pitches(root) == ['C4', 'D4', 'E4', 'F4']
    assert measure_lengths(root) == [4, 4, 4]


def test_grace_before_note():
    root = convert(r"{ \grace d'16 c'1 }")
    assert [x.find('grace') is not None for x in notes(root)] == [True, False]


def graces(root):
    return [n.find('grace') for n in notes(root) if n.find('grace') is not None]


@xfail
def test_after_grace_on_chord():
    root = convert(r"{ \afterGrace <c' e'>2 { d'16 } f'2 }")
    assert pitches(root) == ['C4', 'E4', 'D4', 'F4']
    assert [g.get('steal-time-previous') for g in graces(root)] == ['25']
    assert measure_lengths(root) == [4]
    validate(root)


@xfail
def test_after_grace_at_end_of_measure():
    root = convert(r"{ c'2 \afterGrace d'2 { e'16 f' } | g'1 }")
    m = measures(root)
    assert len(m) == 2
    assert [pitch(n) for n in m[0].findall('note')] == ['C4', 'D4', 'E4', 'F4']
    assert [pitch(n) for n in m[1].findall('note')] == ['G4']


@xfail
def test_after_grace_in_variable():
    root = convert(r"""
orn = \afterGrace c'2 { d'16 }
\score { { \orn e'2 } }
""")
    assert pitches(root) == ['C4', 'D4', 'E4']
    assert [g.get('steal-time-previous') for g in graces(root)] == ['25']


def test_after_grace_with_slur():
    root = convert(r"{ \afterGrace c'2( { d'16 e') } f'2 }")
    slurs = [[s.get('type') for s in n.findall('notations/slur')] for n in notes(root)]
    assert slurs == [['start'], [], ['stop'], []]


@xfail
def test_ordinary_grace_is_not_after_grace():
    root = convert(r"{ \afterGrace c'2 { d'16 } \grace e'16 f'2 }")
    assert [g.get('steal-time-previous') for g in graces(root)] == ['25', None]


@pytest.mark.parametrize('command, slash', [
    (r'\grace', None),
    pytest.param(r'\acciaccatura', 'yes', marks=xfail),
    (r'\appoggiatura', None),
    pytest.param(r'\slashedGrace', 'yes', marks=xfail),
])
def test_grace_slash(command, slash):
    root = convert(r"{ %s d'8 c'2. }" % command)
    assert [g.get('slash') for g in graces(root)] == [slash]
