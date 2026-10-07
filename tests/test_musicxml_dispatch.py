"""Dispatching of ly.music nodes to their handlers in ly.musicxml."""
import pytest

from ly.musicxml.lymus2musxml import ParseSource

from .musicxml_helpers import convert, pitches


def test_attribute_error_in_handler_propagates(monkeypatch):
    def broken(self, rest):
        raise AttributeError('broken handler')
    monkeypatch.setattr(ParseSource, 'Rest', broken)
    with pytest.raises(AttributeError, match='broken handler'):
        convert("{ r4 }")


def test_unimplemented_node_is_reported(capsys):
    root = convert(r"{ \tag #'score c'4 d'4 }")
    assert 'Tag not implemented' in capsys.readouterr().out
    assert pitches(root) == ['C4', 'D4']


# Inputs that exercise many handlers; none of them may raise.
SNIPPETS = [
    r"{ \tweak color #red c'4 d'4 }",
    r"{ \override NoteHead.color = #red c'4 \revert NoteHead.color d'4 }",
    r"{ \once \override Stem.direction = #UP c'4 d'4 }",
    r"{ \set Staff.instrumentName = \markup { Violin } c'1 }",
    r"{ \stemUp c'4 \stemDown d' \stemNeutral e' f' }",
    r"{ \tempo \markup { Allegro } 4 = 120 c'1 }",
    r"{ \ottava #1 c'''4 d''' \ottava #0 e'' f'' }",
    r"{ c'2\startTrillSpan d'\stopTrillSpan }",
    r"{ \repeat tremolo 4 { c'16 e' } c'2 }",
    r"{ c'2\glissando d'2 }",
    r"{ c'4\p\< d' e' f'\f }",
    r"{ c'4^\markup { \bold dolce } d'4_\markup \italic espr. e'2 }",
    r"{ \mark \default c'1 \mark #5 c'1 }",
    r"\drums { bd4 sn hh hh }",
    r'{ \clef "treble_8" c4 \clef bass c, \key fis \minor c2 }',
    r"{ \numericTimeSignature \time 4/4 c'1 }",
    r"{ c'4-1 d'-2 e'-3\fermata f'-4 }",
]


@pytest.mark.parametrize('ly_text', SNIPPETS)
def test_snippet_converts(ly_text):
    convert(ly_text)


# More inputs that exercise handlers, in particular ones whose errors used to
# be hidden by the broad exception handling.
MORE_SNIPPETS = [
    r"{ <>\p c'4 d' e' f' }",
    r"{ \tuplet 3/2 { c'8 d' e' } \times 2/3 { f'4 g' a' } }",
    r"{ \tuplet 3/2 { c'8 \tuplet 3/2 { d'16 e' f' } g'8 } r2. }",
    r"{ \grace c'16 d'4 \acciaccatura e'8 f'4 \appoggiatura g'8 a'4 }",
    r"{ c'4:16 d'2:32 e'4 }",
    r"\new RhythmicStaff { 4 4 8 8 4 }",
    r"{ c'4 4 8 8 4 }",
    r"\header { title = \markup { \bold Title } } { c'1 }",
    r"""{ \bar "|." c'1 }""",
    r"\score { << \new Staff { c'1 } \new FiguredBass \figuremode { <6 4>1 } >> }",
    r"{ \set Staff.instrumentName = \markup { Violin } \unset Staff.instrumentName c'1 }",
    r"\new Staff \with { instrumentName = \markup { Flute } } { c''1 }",
    r"{ \mark \markup { A } c'1 \tempo \markup { Allegro } c'1 }",
    r"{ \override Voice.Glissando.style = #'zigzag c'2\glissando d'2 }",
    r"{ c'4^\markup { \bold \italic dolce } d'4 e'2 }",
]


@pytest.mark.filterwarnings('error')
@pytest.mark.parametrize('ly_text', SNIPPETS + MORE_SNIPPETS)
def test_snippet_converts_without_warnings(ly_text):
    convert(ly_text)


def test_dynamic_on_empty_chord():
    root = convert(r"{ <>\p c'4 d' e' f' }")
    assert root.find('part/measure/direction/direction-type/dynamics/p') is not None


def test_instrument_name_from_markup():
    root = convert(r"{ \set Staff.instrumentName = \markup { Violin } c'1 }")
    assert root.findtext('part-list/score-part/part-name') == 'Violin'
    # the markup is not also written as text
    assert root.find('.//words') is None


def test_tremolo_repeat():
    root = convert(r"{ \repeat tremolo 4 { c'16 e' } c'2 }")
    n = root.findall('part/measure/note')
    assert [x.findtext('type') for x in n] == ['quarter', 'quarter', 'half']
    assert [x.find('notations/ornaments/tremolo').get('type') for x in n[:2]] == ['start', 'stop']


def test_rhythmic_staff():
    root = convert(r"\new RhythmicStaff { 4 4 8 8 4 }")
    assert len(root.findall('part/measure/note')) == 5
