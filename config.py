import os, json, yaml

def load_config(path=None):
    cfg_file = path or os.getenv('REWRITER_CONFIG') or 'config.yaml'
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"Config not found: {cfg_file}")
    with open(cfg_file, 'r') as f:
        return json.load(f) if cfg_file.endswith('.json') else yaml.safe_load(f)
