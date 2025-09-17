import argparse, logging, os
import logging_config
from config import load_config
from input_loader import load_articles
from scaffold_service import scaffold_outline
from framework_service import expand_framework
from hydration_service import hydrate_article
from qc_layer import qc_checks
from qc_reporter import write_qc_report
from output_writer import write_output

def process(entry, cfg, headers, url):
    title = entry['title']
    meta = entry.get('meta', {})
    try:
        o = scaffold_outline(title, meta, cfg['models']['scaffold'], url, headers)
        f = expand_framework(o, cfg['models']['scaffold'], url, headers)
        h = hydrate_article(f, cfg['models']['hydrate'], url, headers)
        errs = qc_checks(h, title, meta)
        entry.update({'article': h, 'qc_errors': errs})
    except Exception as ex:
        logging.error(f"{title} error: {ex}")
        entry.update({'article': '', 'qc_errors': [str(ex)]})
    return entry

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-c', '--config')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging_config.get_logging_config(level=level)

    cfg = load_config(args.config)
    key = cfg['openrouter']['api_key']
    url = cfg['openrouter']['url']
    headers = {'Authorization': f"Bearer {key}", 'Content-Type': 'application/json'}

    entries = load_articles(args.input)

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda e: process(e, cfg, headers, url), entries))

    write_output(results, args.output)
    write_qc_report(results, os.path.splitext(args.output)[0] + '_qc_report.csv')
