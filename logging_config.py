import logging, os
from logging.handlers import TimedRotatingFileHandler

def get_logging_config(log_dir='logs', level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'rewriter.log')
    handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
    formatter = logging.Formatter(
        fmt='{"timestamp":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","message":%(message)s}'
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    return root
