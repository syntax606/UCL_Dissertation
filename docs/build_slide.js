/* Advisory-group intro slide, built to the required template.

   Template: name as the title, then Topic / Question / Status-Approach-findings
   down the left, and an example, setup diagram, preliminary result or pipeline
   on the right. Deliberately plain, matching the supplied format rather than
   the earlier standalone deck, which is preserved in build_slide_detailed.js.

   Usage: NODE_PATH=<path-to-node_modules> node build_slide.js out.pptx
   Bars are shapes, not an embedded chart, because pptxgenjs emits an undeclared
   third axis id and PowerPoint then discards the chart. */

const pptxgen = require("pptxgenjs");

const INK = "1A1A1A";
const BODY = "3C3C3C";
const MUTED = "6E6E6E";
const FAINT = "9A9A9A";
const TEAL = "0F7A84";
const MID = "5E9BA2";
const CLAY = "B4522F";
const RULE = "D8DBDE";
const SANS = "Arial";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Caroline Swartz";
pres.title = "Pragmatic Contrast in Speech Representations";

const s = pres.addSlide();
s.background = { color: "FFFFFF" };

/* ---------------- title ---------------- */

s.addText("Caroline Swartz", {
  x: 0.55, y: 0.42, w: 8, h: 0.6, margin: 0,
  fontFace: SANS, fontSize: 30, color: INK,
});

/* ---------------- left column ---------------- */

const LX = 0.55, LW = 5.75;

s.addText(
  [
    { text: "Topic", options: { bold: true, color: INK } },
    { text: ".  Speech-to-speech systems never receive audio. They receive discrete tokens, so anything the tokeniser discards is unavailable to everything downstream.", options: { color: BODY } },
  ],
  { x: LX, y: 1.55, w: LW, h: 0.8, margin: 0, fontFace: SANS, fontSize: 13, lineSpacingMultiple: 1.18 }
);

s.addText(
  [
    { text: "Question", options: { bold: true, color: INK } },
    { text: ".  The same word can carry opposite force, a sincere ", options: { color: BODY } },
    { text: "yeah", options: { italic: true, color: INK } },
    { text: " against a sarcastic ", options: { color: BODY } },
    { text: "yeah", options: { italic: true, color: INK } },
    { text: ". Is that contrast still present in the representations deployed systems consume, and at which stage of the pipeline is it lost?", options: { color: BODY } },
  ],
  { x: LX, y: 2.45, w: LW, h: 0.95, margin: 0, fontFace: SANS, fontSize: 13, lineSpacingMultiple: 1.18 }
);

s.addText("Status / Approach / findings", {
  x: LX, y: 3.52, w: LW, h: 0.26, margin: 0,
  fontFace: SANS, fontSize: 13, bold: true, color: INK,
});

const bullets = [
  [
    { text: "873 hand-labelled clips drawn from 7,310 hours of podcast audio across eight phrases, with the ", options: { color: BODY } },
    { text: "word held constant", options: { bold: true, color: INK } },
    { text: " so only delivery varies. Linear probes on frozen representations, folds grouped by episode, permutation nulls throughout.", options: { color: BODY } },
  ],
  [
    { text: "Stance is recoverable from continuous encoders and survives every control. A controlled ladder then locates the loss, and ", options: { color: BODY } },
    { text: "quantisation is not where it happens", options: { bold: true, color: INK } },
    { text: ". The codec encoder costs three times what quantisation does, and this replicates on a second codec.", options: { color: BODY } },
  ],
  [
    { text: "The surprise is that ", options: { color: BODY } },
    { text: "distillation helps", options: { bold: true, color: INK } },
    { text: ". DAC, a purely acoustic codec with six times the frame rate, retains half the stance that WavLM-distilled Mimi does. What an encoder is trained on decides what it keeps.", options: { color: BODY } },
  ],
];
bullets.forEach((runs, i) => {
  const y = 3.88 + i * 1.02;
  s.addText("•", {
    x: LX + 0.04, y: y, w: 0.2, h: 0.24, margin: 0,
    fontFace: SANS, fontSize: 13, color: MUTED,
  });
  s.addText(runs, {
    x: LX + 0.28, y: y, w: LW - 0.28, h: 0.95, margin: 0,
    fontFace: SANS, fontSize: 12, lineSpacingMultiple: 1.16,
  });
});

/* ---------------- right column, the result ---------------- */

const RX = 6.95;

s.addText("WHERE THE CONTRAST IS LOST", {
  x: RX, y: 1.55, w: 5.8, h: 0.24, margin: 0,
  fontFace: SANS, fontSize: 11, bold: true, color: TEAL, charSpacing: 0.8,
});
s.addText("Three-way stance, margin over each model's own permutation null. All p ≤ 0.01.", {
  x: RX, y: 1.82, w: 5.8, h: 0.24, margin: 0,
  fontFace: SANS, fontSize: 10, color: MUTED,
});

const BX = RX + 2.15;          // bars start here
const BMAX = 2.55;             // width representing the largest margin
const SCALE = 0.244;
const BH = 0.26;

function bar(y, label, val, colour, bold) {
  s.addText(label, {
    x: RX, y: y - 0.02, w: 2.05, h: BH + 0.04, margin: 0,
    fontFace: SANS, fontSize: 10.5, color: bold ? INK : BODY, bold: !!bold,
    align: "right", valign: "middle",
  });
  s.addShape(pres.ShapeType.rect, {
    x: BX, y: y, w: (val / SCALE) * BMAX, h: BH,
    fill: { color: colour }, line: { width: 0 },
  });
  s.addText("+" + val.toFixed(3), {
    x: BX + (val / SCALE) * BMAX + 0.07, y: y - 0.02, w: 0.75, h: BH + 0.04, margin: 0,
    fontFace: SANS, fontSize: 10.5, bold: true, color: INK, valign: "middle",
  });
}

function drop(y, text) {
  s.addText("↓  " + text, {
    x: BX + 0.06, y: y, w: 3.4, h: 0.24, margin: 0,
    fontFace: SANS, fontSize: 9.5, italic: true, color: CLAY,
  });
}

bar(2.22, "WavLM, continuous", 0.244, TEAL, true);
drop(2.56, "codec encoder and distillation, −0.112");
bar(2.88, "Mimi, before quantisation", 0.132, MID);
drop(3.22, "quantisation, only −0.033");
bar(3.54, "Mimi, after quantisation", 0.099, MID, true);

s.addShape(pres.ShapeType.line, {
  x: RX, y: 4.02, w: 5.8, h: 0, line: { color: RULE, width: 0.75 },
});

bar(4.18, "DAC, after quantisation", 0.087, CLAY);
s.addText("purely acoustic, no distillation, 75 Hz", {
  x: BX + 0.06, y: 4.50, w: 3.4, h: 0.22, margin: 0,
  fontFace: SANS, fontSize: 9.5, italic: true, color: MUTED,
});

s.addText(
  [
    { text: "Read the two drops. ", options: { bold: true, color: INK } },
    { text: "The encoder discards three times what quantisation does, so the token bottleneck is not the bottleneck. And the codec with no semantic distillation keeps less, not more, which inverts the usual expectation that a reconstruction-only codec should preserve paralinguistics best.", options: { color: BODY } },
  ],
  { x: RX, y: 4.92, w: 5.8, h: 1.0, margin: 0, fontFace: SANS, fontSize: 10.5, lineSpacingMultiple: 1.14 }
);

s.addText("MA Computational Linguistics   |   UCL   |   C. Swartz   |   August 2026", {
  x: 0.55, y: 6.85, w: 12.2, h: 0.24, margin: 0,
  fontFace: SANS, fontSize: 9.5, color: FAINT, charSpacing: 0.5,
});

pres.writeFile({ fileName: process.argv[2] || "advisory_slide.pptx" })
  .then(f => console.log("wrote", f));
