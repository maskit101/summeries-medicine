#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בונה מחדש את docs/neurosurgery/index.html, docs/neurosurgery/summaries.html,
ומעדכן את הריבוע של נוירוכירורגיה ב-docs/index.html (עמוד הבית הראשי),
לפי neurosurgery_state.json ו-docs/neurosurgery/flashcards_all.json.

הרץ את הסקריפט הזה בכל פעם שסטטוס פרק משתנה ב-neurosurgery_state.json
(אחרי שנוצרו סיכום/כרטיסיות/PPTX חדשים לפרק).

שימוש: python3 scripts/build_neurosurgery_site.py
(הרץ מתוך שורש הריפו, או מכל מקום - הנתיבים יחסיים למיקום הסקריפט)
"""
import json, re, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPT_DIR)  # repo root
STATE_PATH = os.path.join(BASE, "neurosurgery_state.json")
NS_DIR = os.path.join(BASE, "docs", "neurosurgery")
ROOT_INDEX_PATH = os.path.join(BASE, "docs", "index.html")


def slug(n, title_en):
    s = title_en.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"{n:02d}-{s}"


def main():
    with open(STATE_PATH, encoding="utf-8") as f:
        state = json.load(f)
    chapters = state["chapters"]
    book = state["book"]

    done = [c for c in chapters if c["status"] == "done"]
    pending = [c for c in chapters if c["status"] != "done"]
    pct = round(100 * len(done) / len(chapters)) if chapters else 0

    fc_path = os.path.join(NS_DIR, "flashcards_all.json")
    if os.path.exists(fc_path):
        with open(fc_path, encoding="utf-8") as f:
            fc = json.load(f)
        num_cards = len(fc["cards"])
    else:
        num_cards = 0

    # ---------- summaries.html ----------
    sidebar_items = []
    for c in chapters:
        n = c["n"]; title_he = c.get("title_he", c["title_en"])
        if c["status"] == "done":
            s = slug(n, c["title_en"])
            sidebar_items.append(f'''
            <li class="ch-item done" data-n="{n}">
              <button class="ch-btn" data-n="{n}">
                <div class="ch-num">{n}</div>
                <div class="ch-body">
                  <div class="ch-title">{title_he}</div>
                  <div class="ch-links"><span>📄 סיכום</span></div>
                </div>
              </button>
            </li>''')
        else:
            sidebar_items.append(f'''
            <li class="ch-item pending" data-n="{n}">
              <div class="ch-num">{n}</div>
              <div class="ch-body">
                <div class="ch-title">{title_he}</div>
                <div class="ch-status">בקרוב</div>
              </div>
            </li>''')

    chapters_js = json.dumps([
        {"n": c["n"], "title": c.get("title_he", c["title_en"]), "file": f"summaries/{slug(c['n'], c['title_en'])}.html"}
        for c in done
    ], ensure_ascii=False)

    summaries_html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>סיכומי נוירוכירורגיה - Youmans</title>
<style>
  :root{{color-scheme:light}}
  *{{box-sizing:border-box}}
  html,body{{height:100%; margin:0}}
  body{{font-family:'Segoe UI','Arial Hebrew',sans-serif; background:#f3f4f6; color:#1f2937; display:flex; flex-direction:column}}
  .layout{{display:flex; flex:1; min-height:0}}
  .sidebar{{width:340px; flex-shrink:0; background:#111827; color:#f9fafb; padding:22px 18px; overflow-y:auto; position:relative; transition:width .22s ease, max-height .22s ease}}
  .sidebar-toggle{{position:sticky; top:0; width:34px; height:34px; border-radius:8px; background:#374151; color:#fff; border:none; cursor:pointer; font-size:16px; margin-bottom:14px; display:flex; align-items:center; justify-content:center; flex-shrink:0; z-index:2}}
  .sidebar-toggle:hover{{background:#4b5563}}
  .sidebar.collapsed{{width:52px; padding:14px 9px}}
  .sidebar.collapsed .sidebar-inner{{display:none}}
  .sidebar h2{{font-size:16px; margin:0 0 4px}}
  .sidebar .progress-wrap{{background:#374151; border-radius:6px; height:8px; margin:10px 0 4px; overflow:hidden}}
  .sidebar .progress-bar{{background:#22c55e; height:100%; width:{pct}%}}
  .sidebar .progress-text{{font-size:12.5px; color:#9ca3af; margin-bottom:16px}}
  .ch-list{{list-style:none; padding:0; margin:0}}
  .ch-item{{margin-bottom:4px}}
  .ch-btn{{display:flex; gap:10px; padding:10px 6px; border-radius:8px; width:100%; text-align:start; background:#1f2937; border:none; cursor:pointer; font-family:inherit; color:inherit}}
  .ch-btn:hover{{background:#28344a}}
  .ch-item.done.active .ch-btn{{background:#22c55e; color:#052e16}}
  .ch-item.done.active .ch-btn .ch-num{{background:#052e16; color:#22c55e}}
  .ch-item.done.active .ch-links span{{color:#052e16}}
  .ch-item.pending{{display:flex; gap:10px; padding:10px 6px; border-radius:8px; opacity:.55}}
  .ch-num{{width:24px; height:24px; border-radius:50%; background:#374151; color:#fff; font-size:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0}}
  .ch-item.done .ch-num{{background:#22c55e; color:#052e16}}
  .ch-title{{font-size:13.5px; line-height:1.4}}
  .ch-links{{margin-top:4px; display:flex; gap:10px}}
  .ch-links span{{color:#93c5fd; font-size:12.5px}}
  .ch-status{{font-size:11.5px; color:#6b7280; margin-top:2px}}
  .top-links{{display:flex; flex-direction:column; gap:8px; margin-bottom:18px}}
  .top-links a{{color:#f9fafb; background:#1f2937; border-radius:8px; padding:9px 12px; font-size:13px; text-decoration:none; font-weight:600; display:block}}
  .top-links a:hover{{background:#374151}}
  .top-links a.flashcards{{background:#028090}}
  .top-links a.flashcards:hover{{background:#026e7a}}
  .top-links a.home{{background:transparent; border:1px solid #374151; color:#9ca3af; font-weight:400}}

  main{{flex:1; display:flex; flex-direction:column; min-width:0}}
  .content-nav{{display:none; align-items:center; justify-content:space-between; gap:10px; padding:10px 20px; background:#fff; border-bottom:1px solid #e5e7eb}}
  .content-nav.show{{display:flex}}
  .content-nav .nav-title{{font-size:13.5px; font-weight:700; color:#1f2937; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}}
  .content-nav button{{background:#f3f4f6; border:1px solid #e5e7eb; border-radius:8px; padding:8px 14px; font-size:13px; font-family:inherit; cursor:pointer; color:#1f2937; flex-shrink:0}}
  .content-nav button:hover:not(:disabled){{background:#e5e7eb}}
  .content-nav button:disabled{{opacity:.4; cursor:default}}
  .content-frame{{flex:1; border:none; display:none; background:#fff}}

  .empty-wrap{{flex:1; padding:40px 44px; max-width:760px; overflow-y:auto}}
  .empty-wrap h1{{font-size:28px; margin:0 0 8px}}
  .empty-wrap .sub{{color:#6b7280; margin-bottom:28px}}
  .stat-cards{{display:flex; gap:14px; margin-bottom:28px; flex-wrap:wrap}}
  .stat-card{{background:#fff; border-radius:10px; padding:16px 22px; box-shadow:0 1px 3px rgba(0,0,0,.08); min-width:120px}}
  .stat-card b{{display:block; font-size:26px}}
  .stat-card span{{font-size:13px; color:#6b7280}}
  .latest{{background:#fff; border-radius:10px; padding:20px 24px; box-shadow:0 1px 3px rgba(0,0,0,.08); margin-bottom:20px}}
  .latest h3{{margin-top:0}}
  .latest button.link-btn{{background:none; border:none; padding:0; color:#2563eb; font-weight:600; text-decoration:none; display:block; margin:6px 0; font-size:14.5px; cursor:pointer; font-family:inherit; text-align:start}}
  .latest button.link-btn:hover{{text-decoration:underline}}
  .latest a{{color:#2563eb; font-weight:600; text-decoration:none; display:block; margin:6px 0}}
  .empty{{color:#6b7280}}
  @media (max-width:800px){{
    .layout{{flex-direction:column}}
    .sidebar{{width:100%; max-height:320px}}
    .sidebar.collapsed{{width:100%; max-height:52px; padding:9px}}
    .content-nav button{{padding:10px 14px; font-size:13.5px}}
    .empty-wrap{{padding:24px 18px}}
  }}
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar" id="sidebar">
    <button class="sidebar-toggle" id="sidebarToggle" title="קפל/הרחב תפריט פרקים" aria-label="קפל/הרחב תפריט פרקים">&#9776;</button>
    <div class="sidebar-inner">
      <h2>Youmans Neurological Surgery</h2>
      <div class="progress-wrap"><div class="progress-bar"></div></div>
      <div class="progress-text">{len(done)} / {len(chapters)} פרקים הושלמו ({pct}%)</div>
      <div class="top-links">
        <a class="home" href="../index.html">&#8962; כל הנושאים (עמוד הבית)</a>
        <a class="home" href="index.html">&#8592; עמוד נוירוכירורגיה</a>
        <a class="flashcards" href="flashcards.html">🗂️ כל הכרטיסיות (מאגר מאוחד)</a>
      </div>
      <ul class="ch-list" id="chList">
        {''.join(sidebar_items)}
      </ul>
    </div>
  </nav>
  <main>
    <div class="content-nav" id="contentNav">
      <button id="prevBtn">&#9664; הקודם</button>
      <div class="nav-title" id="navTitle"></div>
      <button id="nextBtn">הבא &#9654;</button>
    </div>
    <iframe id="contentFrame" class="content-frame"></iframe>
    <div class="empty-wrap" id="emptyWrap">
      <h1>סיכומי נוירוכירורגיה</h1>
      <div class="sub">{book} &middot; סיכום + כרטיסיות תרגול לכל פרק, בעברית</div>

      <div class="stat-cards">
        <div class="stat-card"><b>{len(chapters)}</b><span>פרקים ידועים כרגע</span></div>
        <div class="stat-card"><b>{len(done)}</b><span>הושלמו</span></div>
        <div class="stat-card"><b>{len(pending)}</b><span>ממתינים</span></div>
      </div>

      <div class="latest">
        <h3>הפרקים האחרונים שנוספו</h3>
        <div id="latestList"></div>
        <a href="flashcards.html" style="margin-top:6px">🗂️ כל הכרטיסיות של כל הפרקים — מאגר מאוחד אחד</a>
      </div>

      <p style="color:#6b7280; font-size:14px">כל בוקר מתווסף כאן סיכום וחבילת כרטיסיות לפרק הבא בספר, לפי הסדר. השתמשי בתפריט הצד או בכפתורי "הבא/הקודם" כדי לעבור בין הפרקים שכבר הושלמו — התפריט נשאר גלוי כל הזמן. רשימת הפרקים תתעדכן כשיועלו עוד פרקים מהספר.</p>
    </div>
  </main>
</div>

<script>
var CHAPTERS = {chapters_js};

var latestList = document.getElementById('latestList');
if(CHAPTERS.length === 0){{
  latestList.innerHTML = '<p class="empty">עדיין לא נוסף אף סיכום.</p>';
}} else {{
  CHAPTERS.slice(-3).reverse().forEach(function(c){{
    var btn = document.createElement('button');
    btn.className = 'link-btn';
    btn.textContent = 'פרק ' + c.n + ': ' + c.title + ' — סיכום';
    btn.addEventListener('click', function(){{ openChapter(c.n); }});
    latestList.appendChild(btn);
  }});
}}

var frame = document.getElementById('contentFrame');
var emptyWrap = document.getElementById('emptyWrap');
var contentNav = document.getElementById('contentNav');
var navTitle = document.getElementById('navTitle');
var prevBtn = document.getElementById('prevBtn');
var nextBtn = document.getElementById('nextBtn');
var currentN = null;

function indexOfN(n){{ return CHAPTERS.findIndex(function(c){{ return c.n === n; }}); }}

function openChapter(n){{
  var idx = indexOfN(n);
  if(idx === -1) return;
  currentN = n;
  var c = CHAPTERS[idx];
  frame.src = c.file;
  frame.style.display = 'block';
  emptyWrap.style.display = 'none';
  contentNav.classList.add('show');
  navTitle.textContent = 'פרק ' + c.n + ': ' + c.title;
  prevBtn.disabled = (idx === 0);
  nextBtn.disabled = (idx === CHAPTERS.length - 1);

  document.querySelectorAll('.ch-item').forEach(function(li){{ li.classList.remove('active'); }});
  var activeLi = document.querySelector('.ch-item[data-n="' + n + '"]');
  if(activeLi) activeLi.classList.add('active');
}}

prevBtn.addEventListener('click', function(){{
  var idx = indexOfN(currentN);
  if(idx > 0) openChapter(CHAPTERS[idx - 1].n);
}});
nextBtn.addEventListener('click', function(){{
  var idx = indexOfN(currentN);
  if(idx < CHAPTERS.length - 1) openChapter(CHAPTERS[idx + 1].n);
}});

document.querySelectorAll('.ch-btn').forEach(function(btn){{
  btn.addEventListener('click', function(){{ openChapter(parseInt(btn.getAttribute('data-n'), 10)); }});
}});

var sidebarEl = document.getElementById('sidebar');
var sidebarToggle = document.getElementById('sidebarToggle');
var COLLAPSE_KEY = 'ns_sidebar_collapsed';

function setSidebarCollapsed(v){{
  sidebarEl.classList.toggle('collapsed', v);
  try{{ localStorage.setItem(COLLAPSE_KEY, v ? '1' : '0'); }}catch(e){{}}
}}

sidebarToggle.addEventListener('click', function(){{
  setSidebarCollapsed(!sidebarEl.classList.contains('collapsed'));
}});

(function initSidebarState(){{
  var saved = null;
  try{{ saved = localStorage.getItem(COLLAPSE_KEY); }}catch(e){{}}
  if(saved !== null){{ setSidebarCollapsed(saved === '1'); }}
  else if(window.innerWidth < 700){{ setSidebarCollapsed(true); }}
}})();
</script>
</body>
</html>
'''
    with open(os.path.join(NS_DIR, "summaries.html"), "w", encoding="utf-8") as f:
        f.write(summaries_html)

    # ---------- neurosurgery/index.html (2-tile hub) ----------
    index_html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>נוירוכירורגיה - Youmans</title>
<style>
  :root{{color-scheme:light}}
  *{{box-sizing:border-box}}
  body{{font-family:'Segoe UI','Arial Hebrew',sans-serif; margin:0; min-height:100vh; background:#0c1b2a; color:#f1f5f9}}
  .topnav{{padding:18px 24px 0}}
  .topnav a{{color:#7dd3fc; font-size:13.5px; text-decoration:none; font-weight:600}}
  .topnav a:hover{{text-decoration:underline}}
  header{{padding:36px 24px 8px; text-align:center}}
  header h1{{font-size:28px; margin:0 0 8px}}
  header .sub{{color:#93c5fd; font-size:14.5px}}
  .grid{{max-width:720px; margin:32px auto 60px; padding:0 24px; display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:22px}}
  .tile{{display:block; text-decoration:none; color:inherit; border-radius:16px; padding:30px 26px; box-shadow:0 8px 24px rgba(0,0,0,.25); transition:transform .15s, box-shadow .15s}}
  .tile:hover{{transform:translateY(-4px); box-shadow:0 14px 32px rgba(0,0,0,.35)}}
  .tile .icon{{font-size:36px; margin-bottom:14px; display:block}}
  .tile h2{{font-size:20px; margin:0 0 8px}}
  .tile p{{font-size:13.5px; color:rgba(255,255,255,.85); margin:0 0 16px; line-height:1.5}}
  .tile .stat{{background:rgba(255,255,255,.16); border-radius:8px; padding:6px 12px; font-size:12.5px; font-weight:600; display:inline-block}}
  .tile .stat b{{font-size:15px}}
  .tile.summaries{{background:linear-gradient(155deg, #1c7293, #0c1b2a)}}
  .tile.flashcards{{background:linear-gradient(155deg, #028090, #013A40)}}
</style>
</head>
<body>
<div class="topnav"><a href="../index.html">&#8592; כל הנושאים</a></div>
<header>
  <h1>🧠 נוירוכירורגיה</h1>
  <div class="sub">{book}</div>
</header>
<div class="grid">
  <a class="tile summaries" href="summaries.html">
    <span class="icon">📄</span>
    <h2>סיכומים</h2>
    <p>סיכום מעמיק לכל פרק בספר, עם שאלון תרגול — בחירה מתפריט צד לפי פרק</p>
    <div class="stat"><b>{len(done)}/{len(chapters)}</b> פרקים</div>
  </a>
  <a class="tile flashcards" href="flashcards.html">
    <span class="icon">🗂️</span>
    <h2>כרטיסיות</h2>
    <p>בנק כרטיסיות תרגול מאוחד לכל הפרקים, עם סינון, שאלון וסטטיסטיקות</p>
    <div class="stat"><b>{num_cards}</b> כרטיסיות</div>
  </a>
</div>
</body>
</html>
'''
    with open(os.path.join(NS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # ---------- update the neuro tile stats on the root docs/index.html ----------
    if os.path.exists(ROOT_INDEX_PATH):
        with open(ROOT_INDEX_PATH, encoding="utf-8") as f:
            root_html = f.read()
        root_html = re.sub(
            r'(<a class="tile neuro"[^>]*>.*?<div class="stat"><b>)\d+/\d+(</b>פרקים</div>\s*<div class="stat"><b>)\d+(</b>כרטיסיות</div>)',
            rf'\g<1>{len(done)}/{len(chapters)}\g<2>{num_cards}\g<3>',
            root_html, flags=re.S
        )
        with open(ROOT_INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(root_html)

    print(f"Built neurosurgery site — {len(done)}/{len(chapters)} chapters done, {num_cards} cards.")


if __name__ == "__main__":
    main()
