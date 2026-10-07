"""Parts and part groups in the MusicXML export."""
from .musicxml_helpers import convert, parts, pitches, validate


def part_names(root):
    return [p.findtext('part-name') for p in root.findall('part-list/score-part')]


def test_voice_in_staff_group():
    root = convert(r"""\score {
  \new StaffGroup <<
    \new Voice = "S" { \set Staff.instrumentName = #"Cantus" c''2 d'' }
    \new Voice = "B" { \set Staff.instrumentName = #"Bassus" c2 g, }
  >>
}""")
    assert part_names(root) == ['Cantus', 'Bassus']
    assert [pitches(root, i) for i in range(2)] == [['C5', 'D5'], ['C3', 'G2']]
    group = root.findall('part-list/*')
    assert [el.tag for el in group] == ['part-group', 'score-part', 'score-part', 'part-group']
    validate(root)


def test_voices_without_staff():
    root = convert(r"""\score { <<
  \new Voice { e''1 }
  \new Voice { c'1 }
>> }""")
    assert [pitches(root, i) for i in range(len(parts(root)))] == [['E5'], ['C4']]
    validate(root)


def test_single_voice_without_staff():
    root = convert(r"\score { \new Voice { c'1 d'1 } }")
    assert len(parts(root)) == 1
    assert pitches(root) == ['C4', 'D4']
    validate(root)


def test_voices_in_a_staff_share_its_part():
    root = convert(r"""\new Staff <<
  \new Voice { \voiceOne c''1 }
  \new Voice { \voiceTwo a'1 }
>>""")
    assert len(parts(root)) == 1
    assert sorted(pitches(root)) == ['A4', 'C5']
    validate(root)


def test_voice_next_to_staff():
    root = convert(r"""\score { <<
  \new Staff { e''1 }
  \new Voice { c'1 }
>> }""")
    assert [pitches(root, i) for i in range(len(parts(root)))] == [['E5'], ['C4']]
    validate(root)
