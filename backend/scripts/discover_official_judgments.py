#!/usr/bin/env python3
"""Discover official Egyptian judgment documents into a review queue. Never publish automatically."""
import argparse
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
import urllib.robotparser

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOSTS = {"sccourt.gov.eg", "www.sccourt.gov.eg"}
USER_AGENT = "HegazyLegalResearch/0.1 (judgment metadata research; human review required)"
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style"): self.skip+=1
    def handle_endtag(self, tag):
        if tag in ("script","style") and self.skip: self.skip-=1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def urls_from_manifest(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    found=set()
    def walk(x):
        if isinstance(x,dict):
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
        elif isinstance(x,str):
            for u in re.findall(r"https?://[^\\s\\\"'<>]+",x):
                if urllib.parse.urlsplit(u).hostname in OFFICIAL_HOSTS: found.add(u.rstrip(".,;"))
    walk(obj)
    return found

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--limit",type=int,default=20)
    p.add_argument("--fetch",action="store_true",help="Fetch official documents; otherwise only inventory URLs")
    p.add_argument("--out",default="backend/data/judgment_review_queue.json")
    a=p.parse_args()
    candidates=set()
    for path in (ROOT/"backend/data").glob("*.json"):
        try: candidates.update(urls_from_manifest(path))
        except (OSError,ValueError): pass
    records=[]; robots={}
    for url in sorted(candidates)[:max(0,a.limit)]:
        host=urllib.parse.urlsplit(url).hostname
        record={"source_url":url,"source_host":host,"discovered_at":dt.datetime.now(dt.timezone.utc).isoformat(),"status":"needs_human_review","approved_for_publication":False}
        if a.fetch:
            try:
                if host not in robots:
                    rp=urllib.robotparser.RobotFileParser()
                    rp.set_url("https://"+host+"/robots.txt"); rp.read(); robots[host]=rp
                if not robots[host].can_fetch(USER_AGENT,url):
                    record["fetch_status"]="robots_disallowed"
                else:
                    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
                    with urllib.request.urlopen(req,timeout=12) as response:
                        raw=response.read(1_500_000)
                    parser=Extract(); parser.feed(raw.decode("utf-8",errors="replace"))
                    text=" ".join(" ".join(parser.parts).split())
                    record.update(fetch_status="fetched",sha256=hashlib.sha256(raw).hexdigest(),text_excerpt=text[:800])
            except Exception as exc:
                record["fetch_status"]="failed"; record["error_type"]=type(exc).__name__
        records.append(record)
    dest=ROOT/a.out;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({"generated_at":dt.datetime.now(dt.timezone.utc).isoformat(),"total_candidates":len(candidates),"review_required":True,"records":records},ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(f"Queued {len(records)} of {len(candidates)} official URLs for human review; published 0.")

if __name__=="__main__": main()
