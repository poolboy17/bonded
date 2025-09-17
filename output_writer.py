import csv, logging

def write_output(records, path):
    keys = list(records[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    logging.info(f"Output to {path}")
