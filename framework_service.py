import logging, requests
from rate_limiter import RateLimiter

lim_framework = RateLimiter(10, 60)

def expand_framework(outline, model, url, headers):
    prompt = f"Expand outline:\n{outline}"
    lim_framework.acquire()
    r = requests.post(url, headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': prompt}]})
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']
