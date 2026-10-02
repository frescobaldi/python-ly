r"""\repeat volta and \alternative in the MusicXML export."""
import pytest

from .musicxml_helpers import convert, measures, pitches, validate

xfail = pytest.mark.xfail(strict=True, reason="repeats are incomplete")


def barline(measure, location):
    """Return the barline element at location ('left' or 'right') or None."""
    for bl in measure.findall('barline'):
        if bl.get('location', 'right') == location:
            return bl
    return None


def repeat(measure, location):
    bl = barline(measure, location)
    return None if bl is None else bl.find('repeat')


def ending(measure, location):
    """Return (number, type) of the ending at location or None."""
    bl = barline(measure, location)
    if bl is None or bl.find('ending') is None:
        return None
    e = bl.find('ending')
    return e.get('number'), e.get('type')


@xfail
def test_simple_repeat():
    root = convert(r"{ c'1 \repeat volta 2 { d'1 e'1 } f'1 }")
    m = measures(root)
    assert len(m) == 4
    assert repeat(m[0], 'left') is None
    assert repeat(m[1], 'left').get('direction') == 'forward'
    assert repeat(m[2], 'right').get('direction') == 'backward'
    assert repeat(m[3], 'right') is None
    validate(root)


@xfail
def test_repeat_at_start():
    root = convert(r"{ \repeat volta 2 { c'1 } d'1 }")
    m = measures(root)
    assert repeat(m[0], 'left').get('direction') == 'forward'
    assert repeat(m[0], 'right').get('direction') == 'backward'


@xfail
def test_repeat_times():
    root = convert(r"{ \repeat volta 3 { c'1 } }")
    assert repeat(measures(root)[0], 'right').get('times') == '3'


@xfail
@pytest.mark.parametrize('ly_text', [
    r"{ \repeat volta 2 { c'1 } \alternative { { d'1 } { e'1 } } }",
    # LilyPond 2.24 syntax, \alternative inside the repeated music
    r"{ \repeat volta 2 { c'1 \alternative { { d'1 } { e'1 } } } }",
])
def test_alternatives(ly_text):
    root = convert(ly_text)
    m = measures(root)
    assert pitches(root) == ['C4', 'D4', 'E4']
    assert len(m) == 3
    assert repeat(m[0], 'left').get('direction') == 'forward'
    assert repeat(m[0], 'right') is None
    assert ending(m[1], 'left') == ('1', 'start')
    assert ending(m[1], 'right') == ('1', 'stop')
    assert repeat(m[1], 'right').get('direction') == 'backward'
    assert ending(m[2], 'left') == ('2', 'start')
    assert ending(m[2], 'right') == ('2', 'discontinue')
    assert repeat(m[2], 'right') is None
    validate(root)


@xfail
def test_alternative_numbers_with_more_repeats():
    root = convert(r"{ \repeat volta 3 { c'1 } \alternative { { d'1 } { e'1 } } }")
    m = measures(root)
    assert ending(m[1], 'left') == ('1, 2', 'start')
    assert repeat(m[1], 'right').get('times') == '3'
    assert ending(m[2], 'left') == ('3', 'start')


@xfail
def test_alternative_over_several_measures():
    root = convert(r"{ \repeat volta 2 { c'1 } \alternative { { d'1 d'1 } { e'1 } } f'1 }")
    m = measures(root)
    assert len(m) == 5
    assert ending(m[1], 'left') == ('1', 'start')
    assert ending(m[1], 'right') is None
    assert ending(m[2], 'left') is None
    assert ending(m[2], 'right') == ('1', 'stop')
    assert repeat(m[2], 'right').get('direction') == 'backward'
    assert ending(m[3], 'left') == ('2', 'start')
    assert ending(m[3], 'right') == ('2', 'discontinue')
    assert barline(m[4], 'left') is None


def test_unfold_repeat():
    root = convert(r"{ \repeat unfold 2 { c'4 d' } e'2 }")
    assert pitches(root) == ['C4', 'D4', 'C4', 'D4', 'E4']


@xfail
def test_consecutive_repeats():
    root = convert(r"{ \repeat volta 2 { c'1 } \repeat volta 2 { d'1 } }")
    m = measures(root)
    assert len(m) == 2
    for x in m:
        assert repeat(x, 'left').get('direction') == 'forward'
        assert repeat(x, 'right').get('direction') == 'backward'
    validate(root)


@xfail
def test_repeat_of_several_measures_in_three_four():
    root = convert(r"{ \time 3/4 \repeat volta 2 { c'2. d'2. e'2. } }")
    m = measures(root)
    assert len(m) == 3
    assert repeat(m[0], 'left').get('direction') == 'forward'
    assert barline(m[1], 'right') is None
    assert repeat(m[2], 'right').get('direction') == 'backward'


@xfail
def test_repeat_in_every_staff():
    root = convert(r"""\score { <<
  \new Staff { \repeat volta 2 { c''1 } d''1 }
  \new Staff { \repeat volta 2 { c'1 } d'1 }
>> }""")
    for part in (0, 1):
        m = measures(root, part)
        assert repeat(m[0], 'left').get('direction') == 'forward'
        assert repeat(m[0], 'right').get('direction') == 'backward'
        assert barline(m[1], 'left') is None
    validate(root)


@xfail
def test_repeat_in_variable_used_twice():
    root = convert(r"""
rep = \repeat volta 2 { c'1 }
\score { { \rep \rep } }
""")
    m = measures(root)
    assert len(m) == 2
    for x in m:
        assert repeat(x, 'left').get('direction') == 'forward'
        assert repeat(x, 'right').get('direction') == 'backward'


@xfail
def test_alternatives_with_voices():
    root = convert(r"""\new Staff { \repeat volta 2 { << { c''1 } \\ { a'1 } >> }
  \alternative { { d''1 } { e''1 } } }""")
    m = measures(root)
    assert len(m) == 3
    assert ending(m[1], 'left') == ('1', 'start')
    assert ending(m[2], 'right') == ('2', 'discontinue')
    validate(root)


@xfail
def test_three_alternatives():
    root = convert(r"{ \repeat volta 3 { c'1 } \alternative { { d'1 } { e'1 } { f'1 } } }")
    m = measures(root)
    assert [ending(x, 'left') for x in m[1:]] == [('1', 'start'), ('2', 'start'), ('3', 'start')]
    assert [ending(x, 'right') for x in m[1:]] == [('1', 'stop'), ('2', 'stop'), ('3', 'discontinue')]
    assert [repeat(x, 'right') is not None for x in m[1:]] == [True, True, False]
    validate(root)


@xfail
def test_unfold_repeat_with_alternatives():
    root = convert(r"{ \repeat unfold 2 { c'1 } \alternative { { d'1 } { e'1 } } }")
    assert pitches(root) == ['C4', 'D4', 'C4', 'E4']
    assert root.find('.//repeat') is None
    assert root.find('.//ending') is None


@xfail
def test_percent_repeat_is_written_out():
    root = convert(r"{ \repeat percent 2 { c'4 d' e' f' } }")
    assert pitches(root) == ['C4', 'D4', 'E4', 'F4'] * 2
