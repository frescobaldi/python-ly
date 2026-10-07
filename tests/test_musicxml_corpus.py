"""Every snippet of the corpus converts to valid MusicXML."""
import pytest

from .musicxml_corpus import CORPUS, corpus_params
from .musicxml_helpers import convert, validate


@pytest.mark.filterwarnings('error')
@pytest.mark.parametrize('name', corpus_params())
def test_corpus(name):
    validate(convert(CORPUS[name]))
