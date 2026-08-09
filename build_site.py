#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בונה מחדש את outputs/site/index.html מתוך state.json.
הרץ סקריפט זה בכל פעם שסטטוס פרק משתנה ב-state.json (למשל אחרי שנוצר סיכום/כרטיסיות חדשים).
שימוש: python3 build_site.py
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(BASE, "state.json")
SITE_DIR = os.path.join(BASE, "site")
INDEX_PATH = os.path.join(SITE_DIR, "index.html")


def slug(n, title_en):
    import re
    s = title_en.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"{n:02d}-{s}"


def main():
    with open(STATE_PATH, encoding="utf-8") as f:
        state = json.load(f)
    chapters = state["chapters"]

    done = [c for c in chapters if c.get("status") == "done"]
    pending = [c for c in chapters if c.get("status") != "done"]

    sidebar_items = []
    for c in chapters:
        n = c["n"]
        title_he = c.get("title_he", c["title_en"])
        s = slug(n, c["title_en"])
        if c.get("status") == "done":
            sidebar_items.append(f'''
            <li class="ch-item done" data-n="{n}">
              <div class="ch-num">{n}</div>
              <div class="ch-body">
                <div class="ch-title">{title_he}</div>
                <div class="ch-links">
                  <a href="summaries/{s}.html">📄 סיכום</a>
                </div>
              </div>
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

    pct = round(100 * len(done) / len(chapters)) if chapters else 0

    html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<title>סיכומי כירורגיה פלסטית - Neligan Vol.1</title>
<style>
  :root{{color-scheme:light}}
  *{{box-sizing:border-box}}
  body{{font-family:'Segoe UI','Arial Hebrew',sans-serif; margin:0; background:#f3f4f6; color:#1f2937}}
  .layout{{display:flex; min-height:100vh}}
  .sidebar{{width:340px; flex-shrink:0; background:#111827; color:#f9fafb; padding:22px 18px; overflow-y:auto; max-height:100vh; position:sticky; top:0}}
  .sidebar h2{{font-size:16px; margin:0 0 4px}}
  .sidebar .progress-wrap{{background:#374151; border-radius:6px; height:8px; margin:10px 0 4px; overflow:hidden}}
  .sidebar .progress-bar{{background:#22c55e; height:100%; width:{pct}%}}
  .sidebar .progress-text{{font-size:12.5px; color:#9ca3af; margin-bottom:16px}}
  .ch-list{{list-style:none; padding:0; margin:0}}
  .ch-item{{display:flex; gap:10px; padding:10px 6px; border-radius:8px; margin-bottom:4px}}
  .ch-item.done{{background:#1f2937}}
  .ch-item.pending{{opacity:.55}}
  .ch-num{{width:24px; height:24px; border-radius:50%; background:#374151; color:#fff; font-size:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0}}
  .ch-item.done .ch-num{{background:#22c55e; color:#052e16}}
  .ch-title{{font-size:13.5px; line-height:1.4}}
  .ch-links{{margin-top:4px; display:flex; gap:10px}}
  .ch-links a{{color:#93c5fd; font-size:12.5px; text-decoration:none}}
  .ch-links a:hover{{text-decoration:underline}}
  .ch-status{{font-size:11.5px; color:#6b7280; margin-top:2px}}
  .top-links{{display:flex; flex-direction:column; gap:8px; margin-bottom:18px}}
  .top-links a{{color:#f9fafb; background:#1f2937; border-radius:8px; padding:9px 12px; font-size:13px; text-decoration:none; font-weight:600; display:block}}
  .top-links a:hover{{background:#374151}}
  .top-links a.flashcards{{background:#028090}}
  .top-links a.flashcards:hover{{background:#026e7a}}
  .top-links a.home{{background:transparent; border:1px solid #374151; color:#9ca3af; font-weight:400}}

  .main{{flex:1; padding:40px 44px; max-width:760px}}
  .main h1{{font-size:28px; margin:0 0 8px}}
  .main .sub{{color:#6b7280; margin-bottom:28px}}
  .stat-cards{{display:flex; gap:14px; margin-bottom:28px; flex-wrap:wrap}}
  .stat-card{{background:#fff; border-radius:10px; padding:16px 22px; box-shadow:0 1px 3px rgba(0,0,0,.08); min-width:120px}}
  .stat-card b{{display:block; font-size:26px}}
  .stat-card span{{font-size:13px; color:#6b7280}}
  .latest{{background:#fff; border-radius:10px; padding:20px 24px; box-shadow:0 1px 3px rgba(0,0,0,.08); margin-bottom:20px}}
  .latest h3{{margin-top:0}}
  .latest a{{color:#2563eb; font-weight:600; text-decoration:none; display:block; margin:4px 0}}
  .empty{{color:#6b7280}}
  @media (max-width:800px){{ .layout{{flex-direction:column}} .sidebar{{width:100%; max-height:none; position:static}} }}
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <h2>Neligan Vol.1 · Principles</h2>
    <div class="progress-wrap"><div class="progress-bar"></div></div>
    <div class="progress-text">{len(done)} / {len(chapters)} פרקים הושלמו ({pct}%)</div>
    <div class="top-links">
      <a class="home" href="../index.html">&#8592; כל הנושאים</a>
      <a class="flashcards" href="flashcards.html">🗂️ כל הכרטיסיות (מאגר מאוחד)</a>
    </div>
    <ul class="ch-list">
      {''.join(sidebar_items)}
    </ul>
  </nav>
  <main class="main">
    <h1>סיכומי כירורגיה פלסטית</h1>
    <div class="sub">Plastic Surgery, Neligan – כרך 1: Principles &middot; סיכום + כרטיסיות תרגול לכל פרק, בעברית</div>

    <div class="stat-cards">
      <div class="stat-card"><b>{len(chapters)}</b><span>סה"כ פרקים</span></div>
      <div class="stat-card"><b>{len(done)}</b><span>הושלמו</span></div>
      <div class="stat-card"><b>{len(pending)}</b><span>ממתינים</span></div>
    </div>

    <div class="latest">
      <h3>הפרקים האחרונים שנוספו</h3>
      {"".join(f'<a href="summaries/{slug(c["n"], c["title_en"])}.html">פרק {c["n"]}: {c.get("title_he", c["title_en"])} — סיכום</a>' for c in done[-3:][::-1]) or '<p class="empty">עדיין לא נוסף אף סיכום.</p>'}
      <a href="flashcards.html" style="margin-top:6px">🗂️ כל הכרטיסיות של כל הפרקים — מאגר מאוחד אחד</a>
    </div>

    <p style="color:#6b7280; font-size:14px">כל בוקר מתווסף כאן סיכום וחבילת כרטיסיות לפרק הבא בספר, לפי הסדר. השתמשי בתפריט הצד כדי לעבור בין הפרקים שכבר הושלמו.</p>
  </main>
</div>
</body>
</html>
'''

    os.makedirs(SITE_DIR, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built {INDEX_PATH} — {len(done)}/{len(chapters)} done")


if __name__ == "__main__":
    main()
