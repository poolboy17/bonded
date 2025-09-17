# Enterprise Quality Blog Rewriter (Sep 2025) - Unified OpenRouter Implementation
# ------------------------------------------------------------------------
# Single OpenRouter key for both scaffold and hydration stages.
# Modules: config.py, input_loader.py, scaffold_service.py,
# framework_service.py, hydration_service.py, qc_layer.py,
# qc_reporter.py, output_writer.py, rate_limiter.py, main.py

# --- config.py ---
import os, json, yaml

def load_config(path=None):
    cfg_file = path or os.getenv('REWRITER_CONFIG') or 'config.yaml'
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"Config not found: {cfg_file}")
    with open(cfg_file,'r') as f:
        return json.load(f) if cfg_file.endswith('.json') else yaml.safe_load(f)

# --- input_loader.py ---
import pandas as pd, logging

def load_articles(csv_path, required_cols=('title','meta')):
    df = pd.read_csv(csv_path)
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    records=[]
    for idx,row in df.iterrows():
        if pd.isnull(row['title']):
            logging.warning(f"Skipping row {idx}: missing title")
            continue
        records.append({'title':row['title'],'meta':row.get('meta',{})})
    logging.info(f"Loaded {len(records)} articles")
    return records

# --- rate_limiter.py ---
import threading, time
class RateLimiter:
    def __init__(self, max_calls, interval):
        self.lock=threading.Lock()
        self.max=max_calls; self.interval=interval
        self.tokens=self.max; self.ts=time.monotonic()
    def acquire(self):
        with self.lock:
            now=time.monotonic(); elapsed=now-self.ts
            self.tokens=min(self.max,self.tokens+elapsed*(self.max/self.interval))
            self.ts=now
            if self.tokens>=1:
                self.tokens-=1; return
            wait=(1-self.tokens)*(self.interval/self.max)
        time.sleep(wait)
        with self.lock: self.tokens-=1

# --- scaffold_service.py ---
import logging, requests
from rate_limiter import RateLimiter
lim_scaffold=RateLimiter(10,60)
def scaffold_outline(title,meta,model,url,headers):
    prompt=f"Create enterprise outline for Sep2025 '{title}' with meta {meta}."
    lim_scaffold.acquire()
    r=requests.post(url,headers=headers,json={'model':model,'messages':[{'role':'user','content':prompt}]})
    r.raise_for_status()
    out=r.json()['choices'][0]['message']['content']
    logging.debug(out[:50])
    return out

# --- framework_service.py ---
import logging, requests
from rate_limiter import RateLimiter
lim_framework=RateLimiter(10,60)
def expand_framework(outline,model,url,headers):
    prompt=f"Expand outline:\n{outline}"
    lim_framework.acquire()
    r=requests.post(url,headers=headers,json={'model':model,'messages':[{'role':'user','content':prompt}]})
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

# --- hydration_service.py ---
import logging, requests
from rate_limiter import RateLimiter
lim_hydrate=RateLimiter(5,60)
def hydrate_article(framework,model,url,headers):
    prompt=f"Hydrate for enterprise (800+ words):\n{framework}"
    lim_hydrate.acquire()
    r=requests.post(url,headers=headers,json={'model':model,'messages':[{'role':'user','content':prompt}]})
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

# --- qc_layer.py ---
import textstat, re
def qc_checks(text,title,meta):
    errs=[]
    wc=len(text.split());
    if wc<800: errs.append(f"Wordcount {wc}<800")
    if not 45<=len(title)<=70: errs.append(f"Title len {len(title)}")
    if textstat.flesch_reading_ease(text)<50: errs.append("Low readability")
    if len(re.findall(r"^##",text,flags=re.M))<3: errs.append("Few H2s")
    if 'focus_keyword' in meta and meta['focus_keyword'].lower() not in text.lower():
        errs.append("Missing focus keyword")
    if '## FAQ' not in text: errs.append("Missing FAQ")
    return errs

# --- qc_reporter.py ---
import csv, logging
def write_qc_report(recs,path):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['title','qc_errors'])
        for r in recs: w.writerow([r['title'],';'.join(r.get('qc_errors',[]))])
    logging.info(f"QC report at {path}")

# --- output_writer.py ---
import csv, logging
def write_output(recs,path):
    keys=list(recs[0].keys())
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys)
        w.writeheader(); w.writerows(recs)
    logging.info(f"Output to {path}")

# --- main.py ---
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

def process(e,cfg,headers,url):
    t=e['title']; m=e.get('meta',{})
    try:
        o=scaffold_outline(t,m,cfg['models']['scaffold'],url,headers)
        f=expand_framework(o,cfg['models']['scaffold'],url,headers)
        h=hydrate_article(f,cfg['models']['hydrate'],url,headers)
        errs=qc_checks(h,t,m)
        e.update({'article':h,'qc_errors':errs})
    except Exception as ex:
        logging.error(f"{t} error: {ex}")
        e.update({'article':'','qc_errors':[str(ex)]})
    return e

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('-i','--input',required=True)
    p.add_argument('-o','--output',required=True)
    p.add_argument('-c','--config')
    p.add_argument('-v','--verbose',action='store_true')
    args=p.parse_args()
    lvl=logging.DEBUG if args.verbose else logging.INFO
    logging_config.get_logging_config(level=lvl)
    cfg=load_config(args.config)
    key=cfg['openrouter']['api_key']; url=cfg['openrouter']['url']
    hdr={'Authorization':f"Bearer {key}", 'Content-Type':'application/json'}
    entries=load_articles(args.input)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        results=list(ex.map(lambda e: process(e,cfg,hdr,url), entries))
    write_output(results,args.output)
    write_qc_report(results,os.path.splitext(args.output)[0]+'_qc_report.csv')

