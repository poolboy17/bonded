import pytest
from input_loader import load_articles
import pandas as pd

def test_load_articles_valid(tmp_path):
    df = pd.DataFrame({'title':['Test'], 'meta':['{}']})
    file = tmp_path / "in.csv"
    df.to_csv(file, index=False)
    records = load_articles(str(file))
    assert records[0]['title'] == 'Test'

def test_load_articles_missing_column(tmp_path):
    df = pd.DataFrame({'wrong':['X']})
    file = tmp_path / "bad.csv"
    df.to_csv(file, index=False)
    with pytest.raises(ValueError):
        load_articles(str(file))
