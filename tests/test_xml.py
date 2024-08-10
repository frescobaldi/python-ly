"""Tests for XML output."""
import datetime
import difflib
import glob
import ly.musicxml
from lxml import etree
import os
import os.path
import io
import re
import sys


def test_glissando():
    compare_output('glissando')


def test_tie():
    compare_output('tie')


def test_merge_voice():
    compare_output('merge_voice')


def test_variable():
    compare_output('variable')


def test_dynamics():
    compare_output('dynamics')


def test_tuplet():
    compare_output('tuplet')

def test_merge_voice_slurs():
    compare_output('merge_voice_slurs')

def test_break():
    compare_output('break')


def test_mark():
    compare_output('mark')


def test_partial():
    compare_output('partial')


def test_full_bar():
    compare_output('full_bar_rest')


def test_stem_direction():
    compare_output('stem')


def test_church():
    compare_output('church_modes')


def test_markup():
    compare_output('markup')


def test_breathe():
    compare_output('breathe')


def test_no_barcheck():
    compare_output('no_barcheck')


def ly_to_xml(filename):
    """Read Lilypond file and return XML string."""
    writer = ly.musicxml.writer()
    with open(filename, 'r') as lyfile:
        writer.parse_text(lyfile.read())
    xml = writer.musicxml()
    sio = io.BytesIO()
    xml.write(sio, "utf-8")
    return sio.getvalue().decode("utf-8")

encoding_date_element_re = re.compile(r'(?<=<encoding-date>)\d{4}-\d{2}-\d{2}(?=</encoding-date>)')

def read_expected_xml(filename):
    """Return string with expected XML from file."""
    with open(filename, 'r') as xmlfile:
        output = xmlfile.read()
    # Replace date in XML file with today's date
    output = encoding_date_element_re.sub(str(datetime.date.today()), output)
    return output


def compare_output(filename):
    """Compare XML output with expected output."""
    filebase = os.path.join(os.path.dirname(__file__), 'test_xml_files',
                            filename)

    output = ly_to_xml(filebase + '.ly')
    expected_output = read_expected_xml(filebase + '.xml')

    assert_multi_line_equal(expected_output, output)
    validate_xml(output)


def validate_xml(xml):
    """Validate XML against XSD file."""
    xsdname = os.path.join(os.path.dirname(__file__), 'musicxml.xsd')
    xsdfile = open(xsdname, 'r')
    xmlschema_doc = etree.parse(xsdfile)
    xsdfile.close()
    xmlschema = etree.XMLSchema(xmlschema_doc)
    parser = etree.XMLParser(schema=xmlschema)
    # Raises Exception if not valid:
    etree.fromstring(xml, parser)


def assert_multi_line_equal(first, second, msg=None):
    """Assert that two multi-line strings are equal.

    If they aren't, show a nice diff.
    """
    assert isinstance(first, str), 'First argument is not a string'
    assert isinstance(second, str), 'Second argument is not a string'

    if first != second:
        message = ''.join(difflib.ndiff(first.splitlines(True),
                                        second.splitlines(True)))
        if msg:
            message += " : " + msg
        assert False, "Multi-line strings are unequal:\n" + message


def regenerate_xml():
    """Regenerate the XML files"""
    extension_re = re.compile(r'\.ly$')
    for ly_path in glob.glob(os.path.join(os.path.dirname(__file__), 'test_xml_files/*.ly')):
        xml_path = extension_re.sub('.xml', ly_path)
        xml = ly_to_xml(ly_path)
        with open(xml_path, 'w') as fw:
            fw.write(xml)


# Run
#   $ test_xml.py regenerate
# to generate the expected XML files anew with current python-ly
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'regenerate':
        regenerate_xml()
