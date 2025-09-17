import logging, requests
from rate_limiter import RateLimiter

lim_scaffold = RateLimiter(10, 60)

def scaffold_outline(title, meta, model, url, headers):
    prompt = f"Create enterprise outline for Sep2025 '{title}' with meta {meta}."
    lim_scaffold.acquire()
    r = requests.post(url, headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': prompt}]})
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']
