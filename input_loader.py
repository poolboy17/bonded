import pandas as pd, logging

def load_articles(csv_path, required_cols=('title','meta')):
    df = pd.read_csv(csv_path)
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    records = []
    for idx, row in df.iterrows():
        if pd.isnull(row['title']):
            logging.warning(f"Skipping row {idx}: missing title")
            continue
        records.append({'title': row['title'], 'meta': row.get('meta', {})})
    logging.info(f"Loaded {len(records)} articles")
    return records
