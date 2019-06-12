"""Tests for XML output."""
import datetime
import difflib
import ly.musicxml
from lxml import etree
import os
import re
import ly.pkginfo


def test_all():
    """Test all files in test_xml_files"""
    test_list = ['glissando', 'tie', 'merge_voice', 'variable', 'dynamics', 'tuplet', 'pickup', 'lyrics', 'barlines']
    for test in test_list:
        print("Testing {}.ly...".format(test))
        compare_output(test)
        print(test + " test passed.\n")


def ly_to_xml(filename):
    """Read Lilypond file and return XML string."""
    writer = ly.musicxml.writer()
    with open(filename, 'r', encoding='utf-8') as lyfile:
        writer.parse_text(lyfile.read())
    xml = writer.musicxml()
    return (ly.musicxml.create_musicxml.xml_decl_txt.format(encoding='utf-8') + "\n"
        + ly.musicxml.create_musicxml.doctype_txt + "\n"
        + xml.tostring(encoding='unicode'))


def read_expected_xml(filename):
    """Return string with expected XML from file."""
    with open(filename, 'r') as xmlfile:
        output = xmlfile.read()
    # Replace date and python-ly version in XML file with today's date and current version
    output = re.sub(r'\d{4}-\d{2}-\d{2}', str(datetime.date.today()), output)
    output = re.sub(r'python-ly \d*\.\d*\.\d*', "python-ly " + ly.pkginfo.version, output)
    return output


def compare_output(filename):
    """Compare XML output with expected output."""
    filebase = os.path.join(os.path.dirname(__file__), 'test_xml_files',
                            filename)

    output = ly_to_xml(filebase + '.ly')
    expected_output = read_expected_xml(filebase + '.musicxml')

    assert_multi_line_equal(expected_output, output)
    validate_xml(output)


def validate_xml(xml):
    """Validate XML against XSD file."""
    # see https://www.w3.org/2011/prov/track/issues/480
    # and https://stackoverflow.com/questions/49534700/how-to-use-xlink-data-types-in-xsd
    # and https://stackoverflow.com/questions/15830421/xml-unicode-strings-with-encoding-declaration-are-not-supported
    xml = xml.encode('utf-8')
    xsdname = os.path.join(os.path.dirname(__file__), 'musicxml.xsd')
    xmlschema = etree.XMLSchema(file=xsdname)
    parser = etree.XMLParser(schema=xmlschema, encoding='utf-8')
    # Raises Exception if not valid:
    etree.fromstring(xml, parser=parser)


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


if __name__ == "__main__":
    #sys.exit(main(sys.argv))
    test_all()
