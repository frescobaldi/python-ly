"""Chord mode and chord names in the MusicXML export."""
import pytest

from .musicxml_helpers import convert, measure_lengths, measures, parts, validate


def harmony(el):
    """Return (root, alter, kind, bass) of a harmony element."""
    bass = el.findtext('bass/bass-step')
    if bass is not None:
        bass += {0: '', 1: '#', -1: 'b'}[int(el.findtext('bass/bass-alter', '0'))]
    return (el.findtext('root/root-step'),
            int(el.findtext('root/root-alter', '0')),
            el.findtext('kind'),
            bass)


def chords_per_measure(root, part=0):
    """Return the pitches of each chord or single note, grouped per measure."""
    result = []
    for m in measures(root, part):
        groups = []
        for n in m.findall('note'):
            p = n.find('pitch')
            name = p.findtext('step') + {0: '', 1: '#', -1: 'b'}[int(p.findtext('alter', '0'))] + p.findtext('octave')
            if n.find('chord') is not None:
                groups[-1].append(name)
            else:
                groups.append([name])
        result.append(groups)
    return result


@pytest.mark.parametrize('chord, expected', [
    ('c1', ('C', 0, 'major', None)),
    ('c1:m', ('C', 0, 'minor', None)),
    ('g1:7', ('G', 0, 'dominant', None)),
    ('a1:m7', ('A', 0, 'minor-seventh', None)),
    ('c1:maj7', ('C', 0, 'major-seventh', None)),
    ('b1:dim', ('B', 0, 'diminished', None)),
    ('c1:dim7', ('C', 0, 'diminished-seventh', None)),
    ('b1:m7.5-', ('B', 0, 'half-diminished', None)),
    ('c1:aug', ('C', 0, 'augmented', None)),
    ('d1:sus4', ('D', 0, 'suspended-fourth', None)),
    ('c1:6', ('C', 0, 'major-sixth', None)),
    ('c1:9', ('C', 0, 'dominant-ninth', None)),
    ('bes1:7', ('B', -1, 'dominant', None)),
    ('fis1:m', ('F', 1, 'minor', None)),
    ('f1/a', ('F', 0, 'major', 'A')),
    ('c1:7/bes', ('C', 0, 'dominant', 'Bb')),
])
def test_chord_name_kind(chord, expected):
    root = convert(r"\chords { %s }" % chord)
    h = root.findall('.//harmony')
    assert [harmony(e) for e in h] == [expected]
    validate(root)


def test_chord_names_part_timing():
    root = convert(r"\chords { c2 g2:7 f1 }")
    m = measures(root)
    assert [len(x.findall('harmony')) for x in m] == [2, 1]
    assert measure_lengths(root) == [4, 4]
    validate(root)


@pytest.mark.parametrize('chord_names', [
    r"\new ChordNames \chordmode { c2 g2:7 f1 }",
    r"\chords { c2 g2:7 f1 }",
])
def test_chord_names_attach_to_staff(chord_names):
    root = convert(r"""\score { << %s \new Staff { e'4 e' f' f' a'1 } >> }""" % chord_names)
    assert len(parts(root)) == 1
    m = measures(root)
    # every harmony comes directly before the note it belongs to
    tags = [el.tag for el in m[0] if el.tag in ('harmony', 'note')]
    assert tags == ['harmony', 'note', 'note', 'harmony', 'note', 'note']
    assert [harmony(e)[:3] for e in m[0].findall('harmony')] == [
        ('C', 0, 'major'), ('G', 0, 'dominant')]
    assert [harmony(e)[:3] for e in m[1].findall('harmony')] == [('F', 0, 'major')]
    validate(root)


def test_chordmode_in_staff_gives_notes():
    root = convert(r"\new Staff \chordmode { c1 g:7 a:m/c }")
    assert chords_per_measure(root) == [
        [['C3', 'E3', 'G3']],
        [['G3', 'B3', 'D4', 'F4']],
        [['C3', 'A3', 'E4']],
    ]
    assert root.find('.//harmony') is None
    validate(root)


def degrees(el):
    """Return the degrees of a harmony element as (value, alter, type)."""
    return [(int(d.findtext('degree-value')), int(d.findtext('degree-alter')),
             d.findtext('degree-type')) for d in el.findall('degree')]


@pytest.mark.parametrize('chord, kind', [
    ('c1:m6', 'minor-sixth'),
    ('c1:maj9', 'major-ninth'),
    ('c1:m9', 'minor-ninth'),
    ('c1:11', 'dominant-11th'),
    ('c1:13', 'dominant-13th'),
    ('c1:aug7', 'augmented-seventh'),
    ('c1:m7+', 'major-minor'),
    ('c1:sus2', 'suspended-second'),
    ('c1:7.9', 'dominant-ninth'),
])
def test_more_chord_kinds(chord, kind):
    root = convert(r"\chords { %s }" % chord)
    h = root.find('.//harmony')
    assert h.findtext('kind') == kind
    assert degrees(h) == []


@pytest.mark.parametrize('chord, kind, expected', [
    ('c1:7^5', 'dominant', [(5, 0, 'subtract')]),
    ('c1:5.9', 'major', [(9, 0, 'add')]),
    ('c1:7.11+', 'dominant', [(11, 1, 'add')]),
])
def test_chord_degrees(chord, kind, expected):
    root = convert(r"\chords { %s }" % chord)
    h = root.find('.//harmony')
    assert h.findtext('kind') == kind
    assert degrees(h) == expected
    validate(root)


def test_chord_names_with_rests():
    root = convert(r"\chords { c2 r2 g1:7 }")
    assert [len(m.findall('harmony')) for m in measures(root)] == [1, 1]
    assert measure_lengths(root) == [4, 4]
    validate(root)


def test_chordmode_notes():
    root = convert(r"\new Staff \chordmode { c2:m7 c2/+g f1:maj7 }")
    assert chords_per_measure(root) == [
        [['C3', 'Eb3', 'G3', 'Bb3'], ['G2', 'C3', 'E3', 'G3']],
        [['F3', 'A3', 'C4', 'E4']],
    ]


def test_chord_names_attach_to_the_staff_below():
    root = convert(r"""\score { <<
  \chords { c1 g1:7 }
  \new Staff { e'1 d'1 }
  \new Staff { \clef bass c1 g,1 }
>> }""")
    assert len(parts(root)) == 2
    assert len(parts(root)[0].findall('measure/harmony')) == 2
    assert parts(root)[1].find('measure/harmony') is None
    validate(root)


def test_chord_names_in_three_four():
    root = convert(r"""\score { <<
  \new ChordNames \chordmode { \time 3/4 c2. g2.:7 }
  \new Staff { \time 3/4 e'2. d'2. }
>> }""")
    m = measures(root)
    assert len(m) == 2
    assert [[harmony(h)[:3] for h in x.findall('harmony')] for x in m] == [
        [('C', 0, 'major')], [('G', 0, 'dominant')]]
    validate(root)
