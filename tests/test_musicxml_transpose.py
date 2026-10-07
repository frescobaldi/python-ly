r"""\transpose support in the MusicXML export."""
from .musicxml_helpers import convert, pitches, validate


def test_transpose_pitches():
    root = convert(r"\transpose c d { c'4 d' e' fis' }")
    assert pitches(root) == ['D4', 'E4', 'F#4', 'G#4']
    validate(root)


def test_transpose_down_an_octave_and_flat():
    root = convert(r"\transpose c bes, { c'4 d' e' f' }")
    assert pitches(root) == ['Bb3', 'C4', 'D4', 'Eb4']


def test_transpose_relative():
    root = convert(r"\transpose c f \relative c' { c4 e g c }")
    assert pitches(root) == ['F4', 'A4', 'C5', 'F5']


def test_transpose_variable_keeps_other_uses():
    root = convert(r"""
mel = { c'2 e'2 }
\score { { \mel \transpose c es \mel } }
""")
    assert pitches(root) == ['C4', 'E4', 'Eb4', 'G4']


def test_nested_transpose():
    root = convert(r"\transpose c d \transpose c d { c'1 }")
    assert pitches(root) == ['E4']


def test_transpose_key_signature():
    root = convert(r"\transpose c d { \key c \major c'1 }")
    assert root.findtext('part/measure/attributes/key/fifths') == '2'


def test_transpose_chord():
    root = convert(r"\transpose c es { <c' e' g'>1 }")
    assert pitches(root) == ['Eb4', 'G4', 'Bb4']


def test_source_document_is_unchanged():
    import ly.document
    import ly.musicxml
    text = r"\transpose c d { c'4 d' e' f' }"
    doc = ly.document.Document(text)
    writer = ly.musicxml.writer()
    writer.parse_document(doc)
    assert doc.plaintext() == text


def test_transpose_relative_chords():
    root = convert(r"\transpose c d \relative c' { <c e g>4 <d f a> }")
    assert pitches(root) == ['D4', 'F#4', 'A4', 'E4', 'G4', 'B4']


def test_transpose_keeps_spelling_of_the_interval():
    # c -> cis is an augmented unison, so e becomes eis, not f
    root = convert(r"\transpose c cis { c'4 e' g' b' }")
    assert pitches(root) == ['C#4', 'E#4', 'G#4', 'B#4']


def test_transpose_down():
    root = convert(r"\transpose c a, { c'4 e' g' c'' }")
    assert pitches(root) == ['A3', 'C#4', 'E4', 'A4']


def test_transpose_minor_key():
    root = convert(r"\transpose c d { \key a \minor a'1 }")
    key = root.find('part/measure/attributes/key')
    assert key.findtext('fifths') == '2'
    assert key.findtext('mode') == 'minor'


def test_transpose_flat_key():
    root = convert(r"\transpose c es { \key g \major g'1 }")
    assert root.findtext('part/measure/attributes/key/fifths') == '-2'


def test_transpose_chord_repetition():
    root = convert(r"\transpose c d { <c' e'>4 q }")
    assert pitches(root) == ['D4', 'F#4', 'D4', 'F#4']


def test_transpose_isolated_duration():
    root = convert(r"\transpose c d { c'4 4 8 8 }")
    assert pitches(root) == ['D4', 'D4', 'D4', 'D4']


def test_transpose_only_affects_its_staff():
    root = convert(r"""\score { <<
  \new Staff \transpose c d { c'1 }
  \new Staff { c'1 }
>> }""")
    assert pitches(root, 0) == ['D4']
    assert pitches(root, 1) == ['C4']


def test_transpose_ends_with_its_music():
    root = convert(r"{ \transpose c d { c'2 } c'2 }")
    assert pitches(root) == ['D4', 'C4']


def test_transposed_variable_in_score():
    root = convert(r"""
global = { \key c \major \time 2/4 }
melody = \relative c'' { c4 b a2 }
\score { \new Staff \transpose c g, << \global \melody >> }
""")
    assert pitches(root) == ['G4', 'F#4', 'E4']
    assert root.findtext('part/measure/attributes/key/fifths') == '1'
    validate(root)
