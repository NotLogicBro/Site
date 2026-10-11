"""Зеркалит t.me/s/notlogicbro: текст, фото, видео, кружки, голосовые -> posts.json + media/"""
import re, json, os, hashlib, urllib.request
CH = "notlogicbro"
UA = {"User-Agent": "Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
def dl(u):
    if u.startswith("//"): u = "https:" + u
    ext = os.path.splitext(u.split("?")[0])[1] or ".bin"
    p = "media/" + hashlib.md5(u.encode()).hexdigest()[:14] + ext
    if not os.path.exists(p):
        try: open(p, "wb").write(get(u))
        except Exception as e: print("skip", u, e); return None
    return p
def parse(page):
    out = []
    for ch in re.split(r'<div class="tgme_widget_message_wrap', page)[1:]:
        m = re.search(r'data-post="%s/(\d+)"' % CH, ch)
        if not m: continue
        t = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', ch, re.S)
        text = re.sub(r'<script.*?</script>|\son\w+="[^"]*"', '', t.group(1), flags=re.S) if t else ""
        d = re.search(r'<time[^>]+datetime="([^"]+)"', ch)
        rnd = 'tgme_widget_message_roundvideo' in ch
        vids = [dl(x) for x in re.findall(r'<video[^>]+src="([^"]+)"', ch)]
        out.append({
            "id": int(m.group(1)), "date": d.group(1) if d else "", "text": text,
            "photos": [p for p in (dl(x) for x in re.findall(r"tgme_widget_message_photo_wrap[^>]*background-image:url\('([^']+)'\)", ch)) if p],
            "videos": [] if rnd else [v for v in vids if v],
            "rounds": [v for v in vids if v] if rnd else [],
            "voices": [p for p in (dl(x) for x in re.findall(r'<audio[^>]+src="([^"]+)"', ch)) if p],
        })
    return out
old = {p["id"]: p for p in json.load(open("posts.json"))} if os.path.exists("posts.json") else {}
before, pages = None, 6 if not old else 2
for _ in range(pages):
    html = get(f"https://t.me/s/{CH}" + (f"?before={before}" if before else "")).decode("utf-8", "ignore")
    got = parse(html)
    if not got: break
    for p in got: old[p["id"]] = p
    before = min(p["id"] for p in got)
posts = sorted(old.values(), key=lambda p: -p["id"])[:300]
json.dump(posts, open("posts.json", "w"), ensure_ascii=False, indent=1)
print(len(posts), "posts")
