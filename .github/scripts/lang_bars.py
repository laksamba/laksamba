import os, re, json, urllib.request

TOKEN = os.environ["GH_TOKEN"]
OWNER = os.environ["OWNER"]
TOP = 6                      # how many languages to show
EXCLUDE = set()              # e.g. {"HTML", "CSS", "Jupyter Notebook"}
HEAD = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD)) as r:
        return json.load(r)

repos, page = [], 1
while True:
    batch = get(f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner")
    if not batch:
        break
    repos += batch
    page += 1

totals = {}
for r in repos:
    if r["fork"] or r["owner"]["login"].lower() != OWNER.lower():
        continue
    for lang, size in get(r["languages_url"]).items():
        if lang not in EXCLUDE:
            totals[lang] = totals.get(lang, 0) + size

grand = sum(totals.values()) or 1
top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:TOP]

lines = []
for lang, size in top:
    pct = size / grand * 100
    filled = round(pct / 5)          # 20 blocks = 100%
    bar = "█" * filled + "░" * (20 - filled)
    lines.append(f"{lang:<14}{bar}  {pct:5.1f}%")

block = "<!--LANGS:START-->\n```text\n" + "\n".join(lines) + "\n```\n<!--LANGS:END-->"

with open("README.md", encoding="utf-8") as f:
    text = f.read()
text = re.sub(r"<!--LANGS:START-->.*?<!--LANGS:END-->", lambda m: block, text, flags=re.S)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(text)
