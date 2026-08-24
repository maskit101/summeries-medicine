// -*- coding: utf-8 -*-
// בונה PPTX לפרק נוירוכירורגיה בודד מתוך neurosurgery_volN_state.json + docs/neurosurgery/volN/flashcards_all.json.
// שימוש:  node scripts/build_neurosurgery_pptx.js <volume_n> <chapter_n>
// דורש: npm install pptxgenjs (בתיקייה שממנה מריצים, או צריך node_modules נגיש)
// הפלט נשמר ל-docs/neurosurgery/volN/summaries/<NN>-<slug>.pptx

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const volN = parseInt(process.argv[2], 10);
const chapterN = parseInt(process.argv[3], 10);
if (!volN || !chapterN) {
  console.error("Usage: node build_neurosurgery_pptx.js <volume_n> <chapter_n>");
  process.exit(1);
}

const REPO = path.join(__dirname, "..");
const VOL_DIR = path.join(REPO, "docs/neurosurgery", "vol" + volN);
const state = JSON.parse(fs.readFileSync(path.join(REPO, `neurosurgery_vol${volN}_state.json`), "utf8"));
const chapter = state.chapters.find(c => c.n === chapterN);
if (!chapter) { console.error("Chapter not found in state:", chapterN); process.exit(1); }

function slug(n, titleEn) {
  const s = titleEn.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return String(n).padStart(2, "0") + "-" + s;
}

const data = JSON.parse(fs.readFileSync(path.join(VOL_DIR, "flashcards_all.json"), "utf8"));
const cards = data.cards.filter(c => c.id.startsWith(chapterN + "_"));
if (cards.length === 0) { console.error("No cards found with id prefix", chapterN + "_"); process.exit(1); }

// Rotate through a fixed palette by topic_category so each chapter gets consistent, varied colors
const PALETTE_LIST = ["1C7293", "B85042", "21295C", "6D2E46", "2C5F2D", "990011", "028090", "84B59F", "F96167", "69A297"];
const catColorMap = {};
let colorIdx = 0;
function colorFor(cat) {
  if (!catColorMap[cat]) { catColorMap[cat] = PALETTE_LIST[colorIdx % PALETTE_LIST.length]; colorIdx++; }
  return catColorMap[cat];
}

const NAVY = "0C1B2A", TEAL = "1C7293", WHITE = "FFFFFF", DARK = "1F2937", GREEN = "15803D";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.rtlMode = true;

function letterBadge(slide, x, y, letter, color) {
  slide.addShape("ellipse", { x, y, w: 0.4, h: 0.4, fill: { color }, line: { type: "none" } });
  slide.addText(letter, { x, y, w: 0.4, h: 0.4, align: "center", valign: "middle", fontSize: 14, bold: true, color: WHITE, fontFace: "Calibri", rtlMode: true });
}

// ---- Title slide ----
{
  let slide = pres.addSlide();
  slide.background = { color: NAVY };
  slide.addShape("ellipse", { x: 6.08, y: 0.7, w: 1.18, h: 1.18, fill: { type: "none" }, line: { color: TEAL, width: 3 } });
  slide.addShape("ellipse", { x: 6.33, y: 0.95, w: 0.68, h: 0.68, fill: { color: TEAL }, line: { type: "none" } });
  slide.addText("נוירוכירורגיה — כרך " + volN, { x: 1, y: 2.3, w: 11.33, h: 1.0, align: "center", fontSize: 40, bold: true, color: WHITE, fontFace: "Calibri", rtlMode: true });
  slide.addText(`פרק ${chapterN}: ${chapter.title_he || chapter.title_en}`, { x: 1, y: 3.3, w: 11.33, h: 0.7, align: "center", fontSize: 24, color: "93C5FD", fontFace: "Calibri", rtlMode: true });
  slide.addText(chapter.title_en + "  ·  Youmans Neurological Surgery", { x: 1, y: 4.0, w: 11.33, h: 0.5, align: "center", fontSize: 15, italic: true, color: "7DD3FC", fontFace: "Calibri" });
  slide.addText(`${cards.length} כרטיסיות תרגול · שאלה ואז תשובה מלאה בכל כרטיסייה · לסטטיסטיקה חיה השתמשי באפליקציית ה-HTML`, { x: 1, y: 6.5, w: 11.33, h: 0.6, align: "center", fontSize: 12.5, color: "64748B", fontFace: "Calibri", rtlMode: true });
}

cards.forEach((card, idx) => {
  const catColor = colorFor(card.topic_category);
  const he = card.he;
  const letters = ["א", "ב", "ג", "ד"];

  // Question slide
  {
    let slide = pres.addSlide();
    slide.background = { color: WHITE };
    slide.addShape("roundRect", { x: 0.5, y: 0.4, w: 3.4, h: 0.42, rectRadius: 0.08, fill: { color: catColor }, line: { type: "none" } });
    slide.addText(card.topic_category, { x: 0.5, y: 0.4, w: 3.4, h: 0.42, align: "center", valign: "middle", fontSize: 12.5, bold: true, color: WHITE, fontFace: "Calibri", rtlMode: true });
    slide.addText(`כרטיסייה ${idx + 1} מתוך ${cards.length}`, { x: 9.33, y: 0.4, w: 3.4, h: 0.42, align: "left", valign: "middle", fontSize: 12, color: "9CA3AF", fontFace: "Calibri" });
    slide.addText(he.question, { x: 0.6, y: 1.1, w: 12.1, h: 1.6, align: "right", fontSize: 22, bold: true, color: DARK, fontFace: "Calibri", rtlMode: true, valign: "top" });
    let optY = 2.9;
    he.options.forEach((opt, i) => {
      slide.addShape("roundRect", { x: 0.6, y: optY, w: 12.1, h: 0.85, rectRadius: 0.08, fill: { color: "F3F4F6" }, line: { color: "E5E7EB", width: 1 } });
      letterBadge(slide, 11.75, optY + 0.22, letters[i], "6B7280");
      slide.addText(opt, { x: 0.9, y: optY, w: 10.7, h: 0.85, align: "right", valign: "middle", fontSize: 15, color: DARK, fontFace: "Calibri", rtlMode: true, margin: 0 });
      optY += 1.02;
    });
  }

  // Answer slide
  {
    let slide = pres.addSlide();
    slide.background = { color: WHITE };
    slide.addShape("roundRect", { x: 0.5, y: 0.35, w: 3.4, h: 0.4, rectRadius: 0.08, fill: { color: catColor }, line: { type: "none" } });
    slide.addText(card.topic_category, { x: 0.5, y: 0.35, w: 3.4, h: 0.4, align: "center", valign: "middle", fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", rtlMode: true });
    slide.addText(`התשובה הנכונה: ${letters[card.correct_index]}) ${he.options[card.correct_index]}`, { x: 0.6, y: 0.85, w: 12.1, h: 0.7, align: "right", fontSize: 16, bold: true, color: GREEN, fontFace: "Calibri", rtlMode: true, valign: "top" });

    let ay = 1.7;
    slide.addText("מה קורה בפועל:", { x: 8.9, y: ay, w: 3.8, h: 0.35, align: "right", fontSize: 12.5, bold: true, color: "6B7280", fontFace: "Calibri", rtlMode: true });
    ay += 0.4;
    he.answer_lines.forEach((line, i) => {
      const col = line.c || "1C7293";
      slide.addShape("roundRect", { x: 8.9, y: ay, w: 3.8, h: 0.85, rectRadius: 0.07, fill: { color: col, transparency: 88 }, line: { color: col, width: 1.25 } });
      slide.addShape("ellipse", { x: 12.35, y: ay + 0.28, w: 0.28, h: 0.28, fill: { color: col }, line: { type: "none" } });
      slide.addText(line.t, { x: 9.05, y: ay + 0.06, w: 3.15, h: 0.73, align: "right", valign: "middle", fontSize: 9.5, color: DARK, fontFace: "Calibri", rtlMode: true, margin: 0 });
      if (i < he.answer_lines.length - 1) {
        slide.addShape("line", { x: 10.65, y: ay + 0.85, w: 0, h: 0.1, line: { color: "9CA3AF", width: 1.5, endArrowType: "triangle" } });
      }
      ay += 0.95;
    });

    let ly = 1.7;
    slide.addShape("roundRect", { x: 0.6, y: ly, w: 8.1, h: 1.55, rectRadius: 0.06, fill: { color: "F8FAFC" }, line: { color: "E5E7EB", width: 1 } });
    slide.addText("הסבר:", { x: 0.8, y: ly + 0.08, w: 7.7, h: 0.3, align: "right", fontSize: 12, bold: true, color: "6B7280", fontFace: "Calibri", rtlMode: true });
    slide.addText(he.explanation, { x: 0.8, y: ly + 0.38, w: 7.7, h: 1.1, align: "right", fontSize: 10, color: DARK, fontFace: "Calibri", rtlMode: true, valign: "top", margin: 0 });

    let ty = ly + 1.7;
    slide.addShape("roundRect", { x: 0.6, y: ty, w: 8.1, h: 1.0, rectRadius: 0.06, fill: { color: "EFF6FF" }, line: { color: "BFDBFE", width: 1 } });
    slide.addText(`מונח: ${he.term_definition.term}`, { x: 0.8, y: ty + 0.08, w: 7.7, h: 0.3, align: "right", fontSize: 11.5, bold: true, color: "1E3A8A", fontFace: "Calibri", rtlMode: true });
    slide.addText(he.term_definition.text, { x: 0.8, y: ty + 0.4, w: 7.7, h: 0.55, align: "right", fontSize: 9.5, color: "1E3A8A", fontFace: "Calibri", rtlMode: true, valign: "top", margin: 0 });

    let sy = ty + 1.15;
    slide.addShape("roundRect", { x: 0.6, y: sy, w: 8.1, h: 1.55, rectRadius: 0.06, fill: { color: "F5F3FF" }, line: { color: "DDD6FE", width: 1 } });
    slide.addText("סיפור לזכירה", { x: 0.8, y: sy + 0.08, w: 7.7, h: 0.3, align: "right", fontSize: 11.5, bold: true, color: "5B21B6", fontFace: "Calibri", rtlMode: true });
    slide.addText(he.story, { x: 0.8, y: sy + 0.4, w: 7.7, h: 0.55, align: "right", fontSize: 9.5, color: "4C1D95", fontFace: "Calibri", rtlMode: true, valign: "top", margin: 0 });
    slide.addText(`שאלי את עצמך: ${he.why_question.q}`, { x: 0.8, y: sy + 0.97, w: 7.7, h: 0.55, align: "right", fontSize: 9, italic: true, color: "5B21B6", fontFace: "Calibri", rtlMode: true, valign: "top", margin: 0 });

    slide.addText("מצגת סטטית — ללא ניקוד חי. לתרגול עם סטטיסטיקה בזמן אמת, השתמשי באפליקציית ה-HTML (flashcards.html).", { x: 0.6, y: 7.05, w: 12.1, h: 0.35, align: "center", fontSize: 9, italic: true, color: "9CA3AF", fontFace: "Calibri", rtlMode: true });
  }
});

// ---- Closing slide (generic — lists key_terms across all this chapter's cards as a recap) ----
{
  let slide = pres.addSlide();
  slide.background = { color: NAVY };
  slide.addText("סיכום הכרטיסיות", { x: 1, y: 0.6, w: 11.33, h: 0.7, align: "center", fontSize: 30, bold: true, color: WHITE, fontFace: "Calibri", rtlMode: true });
  const terms = [...new Set(cards.flatMap(c => c.he.key_terms || []))].slice(0, 12);
  slide.addText(terms.map(t => ({ text: t, options: { bullet: { code: "25CF" }, breakLine: true, paraSpaceAfter: 12, align: "right", rtlMode: true } })),
    { x: 1.2, y: 1.6, w: 10.93, h: 4.8, fontSize: 16, color: "E5E7EB", fontFace: "Calibri", valign: "top" });
  slide.addText("maskit101.github.io/summeries-medicine/neurosurgery", { x: 1, y: 6.9, w: 11.33, h: 0.4, align: "center", fontSize: 12, color: "64748B", fontFace: "Calibri" });
}

const outName = slug(chapterN, chapter.title_en) + ".pptx";
const outPath = path.join(VOL_DIR, "summaries", outName);
pres.writeFile({ fileName: outPath }).then(() => console.log("Wrote", outPath));
