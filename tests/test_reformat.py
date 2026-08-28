import pytest

import ly.document
import ly.indent
import ly.reformat


def _expect_unchanged(input):
    return (input, input)


@pytest.mark.parametrize('given,expected', [
    ('', ''),
    (' ', ''),
    ("  \\version \"2.24.0\"  ", "\\version \"2.24.0\""),

    ("\\relative { c''4 c \n c c }",
     "\\relative {\n  c''4 c\n  c c\n}"),

    _expect_unchanged("\\version \"2.24.0\" \\score { \\new Staff \\relative { c''4 c c c } }"),
    ("\\score { \n \\new Staff \\relative { c''4 c c c } }",
     "\\score {\n  \\new Staff \\relative { c''4 c c c }\n}"),
    ("\\score { \\new Staff \\relative { c''4 c \n c c } }",
     "\\score {\n  \\new Staff \\relative {\n    c''4 c\n    c c\n  }\n}"),
])
def test_reformat(given, expected):
    indenter = ly.indent.Indenter()

    doc = ly.document.Document(given)
    cursor = ly.document.Cursor(doc)
    ly.reformat.reformat(cursor, indenter)

    assert cursor.text() == expected
