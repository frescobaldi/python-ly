"""Lyrics in the MusicXML export."""
import pytest

from .musicxml_helpers import convert, notes, pitch, validate

xfail = pytest.mark.xfail(strict=True, reason="lyrics support is incomplete")


def lyrics(root):
    """Return (pitch, [(number, syllabic, text, extend), ...]) for every note."""
    return [(pitch(n), [(l.get('number'), l.findtext('syllabic'), l.findtext('text'),
                         l.find('extend') is not None)
                        for l in n.findall('lyric')])
            for n in notes(root)]


def texts(root):
    return [[l.findtext('text') for l in n.findall('lyric')] for n in notes(root)]


def test_syllables_hyphen_and_extender():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4 d' e' f' }
  \new Lyrics \lyricsto "mel" { la -- la __ li lo }
>> }""")
    assert lyrics(root) == [
        ('C4', [('1', 'begin', 'la', False)]),
        ('D4', [('1', 'end', 'la', True)]),
        ('E4', [('1', 'single', 'li', False)]),
        ('F4', [('1', 'single', 'lo', False)]),
    ]
    validate(root)


@xfail
def test_lyrics_context_is_known(capsys):
    convert(r"""\score { <<
  \new Voice = "mel" { c'4 d' }
  \new Lyrics \lyricsto "mel" { a b }
>> }""")
    assert 'not implemented' not in capsys.readouterr().out


@xfail
def test_stanzas_are_numbered():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4 d' }
  \new Lyrics \lyricsto "mel" { a b }
  \new Lyrics \lyricsto "mel" { x y }
>> }""")
    assert [[(l[0], l[2]) for l in ls] for p, ls in lyrics(root)] == [
        [('1', 'a'), ('2', 'x')],
        [('1', 'b'), ('2', 'y')],
    ]
    validate(root)


@xfail
def test_addlyrics():
    root = convert(r"{ c'4 d' e'2 } \addlyrics { a b c }")
    assert texts(root) == [['a'], ['b'], ['c']]


@xfail
def test_addlyrics_twice():
    root = convert(r"{ c'2 d' } \addlyrics { a b } \addlyrics { x y }")
    assert texts(root) == [['a', 'x'], ['b', 'y']]


@xfail
def test_melisma_on_slur_and_tie():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4( d') e' f'~ f'1 }
  \new Lyrics \lyricsto "mel" { a b c }
>> }""")
    assert texts(root) == [['a'], [], ['b'], ['c'], []]


def test_lyrics_skip():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4 d' e' f' }
  \new Lyrics \lyricsto "mel" { a \skip 4 b c }
>> }""")
    assert texts(root) == [['a'], [], ['b'], ['c']]


@xfail
def test_lyricsto_voice_inside_staff():
    root = convert(r"""\score { <<
  \new Staff \new Voice = "mel" { c'4 d' e' f' }
  \new Lyrics \lyricsto "mel" { one two three four }
>> }""")
    assert texts(root) == [['one'], ['two'], ['three'], ['four']]
    validate(root)


def test_rests_get_no_syllable():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4 r d' e' }
  \new Lyrics \lyricsto "mel" { a b c }
>> }""")
    assert texts(root) == [['a'], [], ['b'], ['c']]


@xfail
def test_chord_gets_one_syllable():
    root = convert(r"""\score { <<
  \new Voice = "mel" { <c' e'>4 d' e'2 }
  \new Lyrics \lyricsto "mel" { a b c }
>> }""")
    assert texts(root) == [['a'], [], ['b'], ['c']]


def test_extender_over_slur():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4( d' e') f' }
  \new Lyrics \lyricsto "mel" { la __ li }
>> }""")
    assert lyrics(root) == [
        ('C4', [('1', 'single', 'la', True)]),
        ('D4', []),
        ('E4', []),
        ('F4', [('1', 'single', 'li', False)]),
    ]


@xfail
def test_underscore_is_a_melisma_syllable():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4 d' e' f' }
  \new Lyrics \lyricsto "mel" { a _ b c }
>> }""")
    assert texts(root) == [['a'], [], ['b'], ['c']]


@xfail
def test_lyrics_for_two_voices_in_two_staves():
    root = convert(r"""\score { <<
  \new Staff \new Voice = "s" { e''2 f'' }
  \new Lyrics \lyricsto "s" { up high }
  \new Staff \new Voice = "a" { c''2 d'' }
  \new Lyrics \lyricsto "a" { down low }
>> }""")
    assert [[l.findtext('text') for l in n.findall('lyric')] for n in notes(root, 0)] == [['up'], ['high']]
    assert [[l.findtext('text') for l in n.findall('lyric')] for n in notes(root, 1)] == [['down'], ['low']]
    validate(root)


@xfail
def test_addlyrics_after_staff():
    root = convert(r"\new Staff { c'4 d' e'2 } \addlyrics { x y z }")
    assert texts(root) == [['x'], ['y'], ['z']]


@xfail
def test_stanzas_with_hyphens():
    root = convert(r"""\score { <<
  \new Voice = "mel" { c'4 d' e' f' }
  \new Lyrics \lyricsto "mel" { a -- b c d }
  \new Lyrics \lyricsto "mel" { w x -- y z }
>> }""")
    assert [[(l[0], l[1]) for l in ls] for p, ls in lyrics(root)] == [
        [('1', 'begin'), ('2', 'single')],
        [('1', 'end'), ('2', 'begin')],
        [('1', 'single'), ('2', 'end')],
        [('1', 'single'), ('2', 'single')],
    ]
    validate(root)
