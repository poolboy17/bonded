import pytest
from qc_layer import qc_checks

def test_qc_passes_all():
    text = "## H2\n### H3\n" + "word " * 800 + "Research shows this is test. ## FAQ"
    errors = qc_checks(text, 'Valid Title Length Here', {'focus_keyword':'test'})
    assert errors == []

def test_qc_fails_short():
    errors = qc_checks('short', 'Tiny', {})
    assert any('Wordcount' in e for e in errors)
