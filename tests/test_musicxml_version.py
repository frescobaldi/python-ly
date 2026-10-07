"""MusicXML version of the export."""
import glob
import io
import os.path

import pytest
from lxml import etree

import ly.musicxml

from .musicxml_corpus import CORPUS, corpus_params
from .musicxml_helpers import TESTS_DIR, XSD_4_0, convert, validate

LY_FILES = sorted(glob.glob(os.path.join(TESTS_DIR, 'test_xml_files', '*.ly')))


def write(ly_text):
    writer = ly.musicxml.writer()
    writer.parse_text(ly_text)
    f = io.BytesIO()
    writer.musicxml().write(f)
    return f.getvalue().decode('utf-8')


def test_version_attribute():
    assert convert("{ c'1 }").get('version') == '4.0'


def test_doctype():
    text = write("{ c'1 }")
    assert '"-//Recordare//DTD MusicXML 4.0 Partwise//EN"' in text
    assert '"http://www.musicxml.org/dtds/partwise.dtd"' in text


def test_written_file_is_well_formed():
    etree.fromstring(write("{ c'1 }").encode('utf-8'))


@pytest.mark.parametrize('filename', LY_FILES, ids=os.path.basename)
def test_valid_musicxml_4_0(filename):
    with open(filename) as f:
        validate(convert(f.read()), XSD_4_0)


def test_write_without_doctype():
    writer = ly.musicxml.writer()
    writer.parse_text("{ c'1 }")
    f = io.BytesIO()
    writer.musicxml().write(f, doctype=False)
    text = f.getvalue().decode('utf-8')
    assert text.startswith('<?xml')
    assert '<!DOCTYPE' not in text


def test_write_to_file(tmp_path):
    writer = ly.musicxml.writer()
    writer.parse_text("{ c'1 }")
    filename = str(tmp_path / 'out.musicxml')
    writer.musicxml().write(filename)
    assert etree.parse(filename).getroot().tag == 'score-partwise'


@pytest.mark.parametrize('name', corpus_params())
def test_corpus_valid_musicxml_4_0(name):
    validate(convert(CORPUS[name]), XSD_4_0)
