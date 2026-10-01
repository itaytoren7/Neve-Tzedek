# Builds bizplan.html (a standalone page) from BUSINESS_PLAN.md.
# Run from the repo root:  python3 tools/build_bizplan.py      (needs: pip install markdown)
import os, re, markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md = open(os.path.join(ROOT, 'BUSINESS_PLAN.md'), encoding='utf-8').read()
md = re.sub(r'^<div dir="rtl">\s*|\s*</div>\s*$', '', md.strip())
title_line, _, body_md = md.partition('\n')
title = title_line.lstrip('# ').strip()
body = markdown.markdown(body_md, extensions=['tables', 'sane_lists', 'toc'], extension_configs={'toc': {'toc_depth': '2'}})
body = body.replace('<li>[ ] ', '<li class="task"><span class="box" aria-hidden="true"></span>')
body = re.sub(r'<table>', '<div class="tbl"><table>', body).replace('</table>', '</table></div>')
body = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" /></p>', r'<figure><img src="\2" alt="\1" loading="lazy"><figcaption>\1</figcaption></figure>', body)
toc = ''.join(f'<a href="#{m.group(1)}">{m.group(2)}</a>' for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body))
first_p = re.search(r'<p>(.*?)</p>', body).group(1)
byline = re.sub('<[^>]+>', '', first_p)
body = body.replace(f'<p>{first_p}</p>', '', 1)

PAGE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>תכנית עסקית · שבזי 58</title>
<meta name="description" content="תכנית עסקית לנכס לשימור בשבזי 58 / אחד העם 1, נווה צדק: זכויות, שימור, חלופות, מודל פיננסי והמלצה.">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/brand/favicon-16.png">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<meta name="theme-color" content="#faf7f0">
<meta property="og:type" content="website">
<meta property="og:site_name" content="שבזי 58 · אחד העם 1">
<meta property="og:title" content="תכנית עסקית · שבזי 58">
<meta property="og:description" content="תכנית עסקית לנכס לשימור בשבזי 58 / אחד העם 1, נווה צדק: זכויות, שימור, חלופות, מודל פיננסי והמלצה.">
<meta property="og:url" content="https://itaytoren7.github.io/Neve-Tzedek/bizplan.html">
<meta property="og:image" content="https://itaytoren7.github.io/Neve-Tzedek/assets/brand/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Hebrew:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* Layout: one reading column with a sticky section index on the reading edge; same palette as the 3D model page. */
:root{
  --bg:#f4f5f2; --surface:#ffffff; --surface-2:#eef0ec; --line:#d9ddd6; --fg:#1b221e; --muted:#5b6660;
  --accent:#2d6d61; --accent-soft:rgba(45,109,97,.10);
  --font-display:"Frank Ruhl Libre","David Libre","Times New Roman",serif;
  --font-body:"IBM Plex Sans Hebrew","Heebo","Arial Hebrew",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  color-scheme:light;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#101412; --surface:#171c19; --surface-2:#1e2420; --line:#2c3530; --fg:#e3e9e5; --muted:#98a39c;
  --accent:#6cbfac; --accent-soft:rgba(108,191,172,.12); color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#101412; --surface:#171c19; --surface-2:#1e2420; --line:#2c3530; --fg:#e3e9e5; --muted:#98a39c;
  --accent:#6cbfac; --accent-soft:rgba(108,191,172,.12); color-scheme:dark }
*{box-sizing:border-box}
html{scroll-padding-top:72px}
body{margin:0; background:var(--bg); color:var(--fg); font-family:var(--font-body); font-size:16px; line-height:1.7}
a{color:var(--accent)}
a:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.bar{position:sticky; top:0; z-index:5; background:color-mix(in srgb, var(--bg) 90%, transparent); backdrop-filter:blur(8px); border-bottom:1px solid var(--line)}
.bar .in{max-width:1180px; margin:0 auto; padding-inline:16px; padding-block:10px; display:flex; align-items:center; gap:12px; flex-wrap:wrap}
.bar b{font-family:var(--font-display); font-size:17px}
.bar .sp{margin-inline-start:auto; display:flex; gap:8px; flex-wrap:wrap}
.btn{font-size:13.5px; font-weight:600; border-radius:999px; padding:6px 14px; border:1px solid var(--line); background:var(--surface); color:var(--fg); text-decoration:none; white-space:nowrap}
.btn:hover{border-color:var(--accent); color:var(--accent)}
.btn.primary{background:var(--accent); border-color:var(--accent); color:var(--surface)}
.wrap{max-width:1180px; margin:0 auto; padding-inline:16px; padding-block:28px 64px; display:grid; grid-template-columns:230px minmax(0,1fr); gap:40px}
nav{position:sticky; top:76px; align-self:start; max-height:calc(100vh - 96px); overflow-y:auto; font-size:13.5px}
.toc summary{font-size:11.5px; letter-spacing:.06em; color:var(--muted); font-weight:600; margin-bottom:6px; cursor:pointer; list-style:none}
.toc summary::-webkit-details-marker{display:none}
.toc .links{display:flex; flex-direction:column; gap:2px}
.toc a{color:var(--muted); text-decoration:none; padding:4px 10px; border-inline-start:2px solid transparent; border-radius:0 6px 6px 0}
.toc a:hover{color:var(--accent); border-inline-start-color:var(--accent); background:var(--accent-soft)}
article{min-width:0; max-width:780px}
header.doc h1{font-family:var(--font-display); font-weight:700; font-size:clamp(28px,4.2vw,40px); line-height:1.15; margin:0 0 6px; text-wrap:balance}
header.doc .by{color:var(--muted); font-size:14px; margin-bottom:10px}
header.doc .brand{display:block; height:150px; width:auto; margin:0 0 18px}
h2{font-family:var(--font-display); font-size:26px; line-height:1.25; margin:48px 0 10px; padding-top:18px; border-top:1px solid var(--line); text-wrap:balance}
h3{font-size:17px; margin:26px 0 6px}
p,li{max-width:68ch}
ul,ol{padding-inline-start:22px}
li{margin:3px 0}
strong{font-weight:600}
.tbl{overflow-x:auto; margin:14px 0; border:1px solid var(--line); border-radius:10px; background:var(--surface)}
table{border-collapse:collapse; width:100%; font-size:14px; line-height:1.5}
th,td{padding:8px 11px; border-bottom:1px solid var(--line); text-align:start; vertical-align:top}
tr:last-child td{border-bottom:none}
th{background:var(--surface-2); color:var(--muted); font-weight:600; font-size:13px}
td{font-variant-numeric:tabular-nums}
figure{margin:20px 0; background:#fff; border:1px solid var(--line); border-radius:12px; padding:10px; overflow-x:auto}
figure img{display:block; width:100%; min-width:560px; height:auto}
figcaption{font-size:12.5px; color:#5b6660; padding:6px 4px 0}
li.task{list-style:none; margin-inline-start:-22px; display:flex; gap:10px; align-items:flex-start}
li.task .box{flex:0 0 16px; height:16px; margin-top:5px; border:1.5px solid var(--muted); border-radius:4px}
hr{border:none; border-top:1px solid var(--line); margin:40px 0 16px}
code{font-family:var(--font-mono); font-size:.9em; background:var(--surface-2); padding:1px 5px; border-radius:4px}
.note{font-size:13px; color:var(--muted)}
@media (max-width: 900px){ .wrap{grid-template-columns:minmax(0,1fr)} nav{position:static; max-height:none} .toc{border:1px solid var(--line); border-radius:10px; padding:8px 12px; background:var(--surface)} .toc summary{margin:0; font-size:13.5px} .toc summary::after{content:" ▾"} .toc[open] .links{margin-top:8px} }
@media (prefers-reduced-motion: no-preference){ html{scroll-behavior:smooth} }
</style>
</head>
<body>
<div class="bar"><div class="in"><b>שבזי 58 · אחד העם 1</b><span class="note">נווה צדק · גוש 7422 · חלקות 47–48</span>
<div class="sp"><a class="btn" href="index.html">הדמיה תלת-ממדית</a><a class="btn" href="data/zchuyot/zchuyot_gush7422_helka47.pdf">דף זכויות 47</a><a class="btn" href="data/zchuyot/zchuyot_gush7422_helka48.pdf">דף זכויות 48</a></div></div></div>
<div class="wrap">
<nav aria-label="תוכן העניינים"><details class="toc" id="toc" open><summary>תוכן</summary><div class="links">__TOC__</div></details></nav>
<article>
<header class="doc"><img class="brand" src="assets/brand/logo.png" alt="שבזי 58 · Ahad Ha'Am 1" width="685" height="899"><h1>__TITLE__</h1><div class="by">__BYLINE__</div></header>
__BODY__
</article>
</div>
<script>try{ if (window.matchMedia('(max-width: 900px)').matches) document.getElementById('toc').removeAttribute('open'); }catch(e){}</script>
</body>
</html>
'''
html = PAGE.replace('__TOC__', toc).replace('__TITLE__', title).replace('__BYLINE__', byline).replace('__BODY__', body)
open(os.path.join(ROOT, 'bizplan.html'), 'w', encoding='utf-8').write(html)
print('wrote bizplan.html', len(html))
