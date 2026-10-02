"""Header fields and unpitched notes in the MusicXML export."""
from .musicxml_helpers import convert, notes, validate


def test_header_fields():
    root = convert(r"""\header {
  title = "T" composer = "C" arranger = "A" poet = "P"
  copyright = "CC" opus = "Op. 1" piece = "Piece"
}
{ c'1 }""")
    assert root.findtext('movement-title') == 'T'
    ident = root.find('identification')
    assert [el.tag for el in ident] == [
        'creator', 'creator', 'creator', 'rights', 'encoding', 'miscellaneous']
    assert [(c.get('type'), c.text) for c in ident.findall('creator')] == [
        ('composer', 'C'), ('arranger', 'A'), ('poet', 'P')]
    assert ident.findtext('rights') == 'CC'
    assert [(f.get('name'), f.text) for f in ident.findall('miscellaneous/miscellaneous-field')] == [
        ('opus', 'Op. 1'), ('piece', 'Piece')]
    validate(root)


def test_unpitched_note_element_order():
    root = convert(r"\new DrumStaff \drummode { bd4. sn8 hh2 }")
    for n in notes(root):
        tags = [el.tag for el in n]
        assert tags.index('voice') < tags.index('type')
    validate(root)


def test_drum_chords():
    root = convert(r"\new DrumStaff \drummode { <bd hh>4 <sn hh> r2 }")
    n = notes(root)
    assert [x.find('chord') is not None for x in n] == [False, True, False, True, False]
    assert [x.findtext('type') for x in n[:4]] == ['quarter'] * 4
    validate(root)
