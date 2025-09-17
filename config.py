import os, json, yaml

def load_config(path=None):
    cfg_file = path or os.getenv('REWRITER_CONFIG') or 'config.yaml'
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"Config not found: {cfg_file}")
    with open(cfg_file, 'r') as f:
        cfg = json.load(f) if cfg_file.endswith('.json') else yaml.safe_load(f)
    # Substitute environment variable for openrouter.api_key if needed
    if (
        'openrouter' in cfg and
        isinstance(cfg['openrouter'], dict) and
        isinstance(cfg['openrouter'].get('api_key'), str) and
        cfg['openrouter']['api_key'].startswith('${')
    ):
        env_var = cfg['openrouter']['api_key'][2:-1]
        cfg['openrouter']['api_key'] = os.getenv(env_var, cfg['openrouter']['api_key'])
    return cfg
