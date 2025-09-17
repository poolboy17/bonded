import logging, requests
from rate_limiter import RateLimiter

lim_hydrate = RateLimiter(5, 60)

def hydrate_article(framework, model, url, headers):
    prompt = f"Hydrate for enterprise (800+ words):\n{framework}"
    lim_hydrate.acquire()
    r = requests.post(url, headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': prompt}]})
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']
