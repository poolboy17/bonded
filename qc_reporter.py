import csv, logging

def write_qc_report(records, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'qc_errors'])
        for r in records:
            writer.writerow([r['title'], ';'.join(r.get('qc_errors', []))])
    logging.info(f"QC report at {path}")
