"""Helpers for semantic tests of the LilyPond to MusicXML export.

The tests built on these helpers look at the parts of the MusicXML output they
are about (pitches, durations, barlines, ...) instead of comparing whole files.
"""
import os.path
from fractions import Fraction

from lxml import etree

import ly.musicxml


TESTS_DIR = os.path.dirname(__file__)
XSD_3_0 = os.path.join(TESTS_DIR, 'musicxml.xsd')
XSD_4_0 = os.path.join(TESTS_DIR, 'musicxml-4.0', 'musicxml.xsd')

_schemas = {}


def convert(ly_text):
    """Convert LilyPond text and return the root element of the MusicXML."""
    writer = ly.musicxml.writer()
    writer.parse_text(ly_text)
    return etree.fromstring(writer.musicxml().tostring())


def validate(root, xsd=XSD_3_0):
    """Raise etree.DocumentInvalid if root is not valid against xsd."""
    if xsd not in _schemas:
        _schemas[xsd] = etree.XMLSchema(etree.parse(xsd))
    _schemas[xsd].assertValid(root)


def parts(root):
    return root.findall('part')


def measures(root, part=0):
    return parts(root)[part].findall('measure')


def notes(root, part=0):
    return parts(root)[part].findall('measure/note')


def pitch(note):
    """Return the pitch of a note element as e.g. 'C4', 'F#4' or 'Bb3'.

    Rests are returned as 'r'.
    """
    if note.find('rest') is not None:
        return 'r'
    p = note.find('pitch')
    alter = {-2: 'bb', -1: 'b', 0: '', 1: '#', 2: '##'}[int(p.findtext('alter', '0'))]
    return p.findtext('step') + alter + p.findtext('octave')


def pitches(root, part=0, voice=None):
    """Return the pitches of all notes in a part, optionally only of one voice."""
    return [pitch(n) for n in notes(root, part)
            if voice is None or n.findtext('voice') == str(voice)]


def divisions(root, part=0):
    return int(parts(root)[part].findtext('measure/attributes/divisions'))


def quarters(root, part=0):
    """Return a function that converts a duration in divisions to quarters."""
    div = divisions(root, part)
    return lambda duration: Fraction(int(duration), div)


def voice_lengths(measure, div):
    """Return a dict mapping each voice to its length in quarter notes.

    Chord notes and grace notes are not counted; <backup> and <forward>
    move the current position, as in MusicXML.
    """
    lengths = {}
    pos = Fraction(0)
    for el in measure:
        if el.tag == 'note':
            if el.find('chord') is not None or el.find('grace') is not None:
                continue
            pos += Fraction(int(el.findtext('duration')), div)
            voice = el.findtext('voice', '1')
            lengths[voice] = max(lengths.get(voice, 0), pos)
        elif el.tag == 'backup':
            pos -= Fraction(int(el.findtext('duration')), div)
        elif el.tag == 'forward':
            pos += Fraction(int(el.findtext('duration')), div)
            voice = el.findtext('voice', '1')
            lengths[voice] = max(lengths.get(voice, 0), pos)
    return lengths


def measure_lengths(root, part=0):
    """Return the length of every measure in quarter notes.

    The length of a measure is the length of its longest voice.
    """
    div = divisions(root, part)
    return [max(voice_lengths(m, div).values(), default=0)
            for m in measures(root, part)]
