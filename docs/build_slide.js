/* Advisory-group slide generator.
   Usage: NODE_PATH=<path-to-node_modules> node build_slide.js out.pptx
   Bars are drawn as shapes rather than an embedded chart object, because
   pptxgenjs emits an undeclared third axis id for this configuration and
   PowerPoint then discards the chart. */

const pptxgen = require("pptxgenjs");

const INK = "131920";
const MUTED = "5C6773";
const FAINT = "8A94A1";
const TEAL = "0F7A84";
const TEAL_TINT = "EAF2F3";
const CLAY = "B4522F";
const GREY_BAR = "94A0AE";
const CARD = "F4F6F7";
const RULE = "DDE1E7";

const SERIF = "Cambria";
const SANS = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Caroline Swartz";
pres.title = "Pragmatic Contrast in Speech Representations";

const s = pres.addSlide();
s.background = { color: "FFFFFF" };

/* ---------------- header ---------------- */

s.addText("Transcript-Equivalent Pragmatic Contrast in Speech Representations", {
  x: 0.5, y: 0.24, w: 12.3, h: 0.55, margin: 0,
  fontFace: SERIF, fontSize: 26, bold: true, color: INK,
});

s.addText(
  "Deployed speech-to-speech systems never hear raw audio. They hear discrete tokens. Do those tokens still retain untranscribed meaning?",
  {
    x: 0.5, y: 0.84, w: 12.3, h: 0.38, margin: 0,
    fontFace: SERIF, fontSize: 14, italic: true, color: TEAL,
  }
);

s.addText("MA Computational Linguistics   |   UCL   |   C. Swartz   |   July 2026", {
  x: 0.5, y: 1.20, w: 12.3, h: 0.24, margin: 0,
  fontFace: SANS, fontSize: 9.5, color: FAINT, charSpacing: 0.6,
});

/* ---------------- why this experiment, the three-step chain ---------------- */

const CHAIN_Y = 1.56;
const COLW = 3.91;
const COLX = [0.5, 4.69, 8.88];

s.addShape(pres.ShapeType.line, {
  x: 0.5, y: CHAIN_Y - 0.10, w: 12.3, h: 0,
  line: { color: RULE, width: 0.75 },
});

const heads = ["Established", "The confound", "This study"];
heads.forEach((h, i) => {
  s.addShape(pres.ShapeType.ellipse, {
    x: COLX[i], y: CHAIN_Y, w: 0.19, h: 0.19,
    fill: { color: TEAL }, line: { width: 0 },
  });
  s.addText(String(i + 1), {
    x: COLX[i], y: CHAIN_Y, w: 0.19, h: 0.19, margin: 0,
    fontFace: SANS, fontSize: 8.5, bold: true, color: "FFFFFF",
    align: "center", valign: "middle",
  });
  s.addText(h.toUpperCase(), {
    x: COLX[i] + 0.27, y: CHAIN_Y - 0.01, w: COLW - 0.27, h: 0.21, margin: 0,
    fontFace: SANS, fontSize: 9.5, bold: true, color: INK,
    charSpacing: 1.0, valign: "middle",
  });
});

s.addText(
  [
    { text: "Speech representations recover pragmatic phenomena better than text, shown by ", options: { color: MUTED } },
    { text: "Lin et al. (2022)", options: { bold: true, color: INK } },
    { text: " probing self-supervised models on sarcasm. Separately, discretisation is known to damage paralinguistic content (DASB, Mousavi et al. 2026).", options: { color: MUTED } },
  ],
  { x: COLX[0], y: CHAIN_Y + 0.28, w: COLW, h: 0.92, margin: 0, fontFace: SANS, fontSize: 9.5, lineSpacingMultiple: 1.08 }
);

s.addText(
  [
    { text: "Lin et al. probed ", options: { color: MUTED } },
    { text: "MUStARD", options: { bold: true, color: INK } },
    { text: ", where the utterances also differ in their words, so delivery stays confounded with word choice. That corpus is acted television speech, carries one binary sarcasm label, and no discrete tokeniser was compared.", options: { color: MUTED } },
  ],
  { x: COLX[1], y: CHAIN_Y + 0.28, w: COLW, h: 0.92, margin: 0, fontFace: SANS, fontSize: 9.5, lineSpacingMultiple: 1.08 }
);

const maps = [
  ["words vary", "word held constant"],
  ["acted speech", "naturalistic podcast audio"],
  ["one binary label", "stance and arousal on separate axes"],
  ["continuous only", "Mimi, what deployed systems consume"],
];
s.addText(
  maps.flatMap(([was, now], i) => ([
    { text: was, options: { strike: true, color: FAINT } },
    { text: "   →   ", options: { color: TEAL, bold: true } },
    { text: now, options: { color: INK, breakLine: i < maps.length - 1 } },
  ])),
  { x: COLX[2], y: CHAIN_Y + 0.28, w: COLW, h: 0.92, margin: 0, fontFace: SANS, fontSize: 9.5, lineSpacingMultiple: 1.22 }
);

/* ---------------- left card, the design move ---------------- */

const CX = 0.5, CY = 2.82, CW = 4.05, CH = 3.62;

s.addShape(pres.ShapeType.roundRect, {
  x: CX, y: CY, w: CW, h: CH,
  fill: { color: CARD }, line: { color: RULE, width: 0.75 }, rectRadius: 0.06,
});

s.addText("THE DESIGN MOVE, LEXICAL CONTROL", {
  x: CX + 0.22, y: CY + 0.13, w: CW - 0.44, h: 0.22, margin: 0,
  fontFace: SANS, fontSize: 9, bold: true, color: TEAL, charSpacing: 1.1,
});

s.addText("yeah", {
  x: CX + 0.22, y: CY + 0.42, w: 1.5, h: 0.55, margin: 0,
  fontFace: SERIF, fontSize: 28, bold: true, color: TEAL, align: "center",
});
s.addText("vs", {
  x: CX + 1.72, y: CY + 0.57, w: 0.4, h: 0.26, margin: 0,
  fontFace: SANS, fontSize: 10, color: FAINT, align: "center",
});
s.addText("yeah", {
  x: CX + 2.12, y: CY + 0.42, w: 1.5, h: 0.55, margin: 0,
  fontFace: SERIF, fontSize: 28, bold: true, italic: true, color: CLAY, align: "center",
});

s.addText("SINCERE AGREEMENT", {
  x: CX + 0.10, y: CY + 0.99, w: 1.74, h: 0.20, margin: 0,
  fontFace: SANS, fontSize: 8, bold: true, color: MUTED, align: "center", charSpacing: 0.5,
});
s.addText("SARCASTIC DISMISSAL", {
  x: CX + 2.00, y: CY + 0.99, w: 1.74, h: 0.20, margin: 0,
  fontFace: SANS, fontSize: 8, bold: true, color: MUTED, align: "center", charSpacing: 0.5,
});

s.addText("Identical word, different meaning.", {
  x: CX + 0.22, y: CY + 1.25, w: CW - 0.44, h: 0.24, margin: 0,
  fontFace: SERIF, fontSize: 12, italic: true, color: INK, align: "center",
});

s.addShape(pres.ShapeType.line, {
  x: CX + 0.22, y: CY + 1.56, w: CW - 0.44, h: 0,
  line: { color: RULE, width: 0.75 },
});

/* sampling funnel, read top to bottom */
const funnel = [
  ["7,310", "hours of podcast audio indexed, 6,281 episodes"],
  ["767k", "occurrences of the eight phrases after filtering"],
  ["873", "hand-labelled clips across 753 episodes"],
];
funnel.forEach(([n, k], i) => {
  const y = CY + 1.66 + i * 0.36;
  s.addText(n, {
    x: CX + 0.22, y: y, w: 0.80, h: 0.30, margin: 0,
    fontFace: SANS, fontSize: 15, bold: true, color: i === 2 ? TEAL : INK,
    align: "right", valign: "middle",
  });
  s.addText(k, {
    x: CX + 1.10, y: y, w: 2.68, h: 0.30, margin: 0,
    fontFace: SANS, fontSize: 8.5, color: MUTED, valign: "middle",
  });
  if (i < 2) {
    s.addText("↓", {
      x: CX + 0.22, y: y + 0.21, w: 0.80, h: 0.16, margin: 0,
      fontFace: SANS, fontSize: 8, color: FAINT, align: "right",
    });
  }
});

/* controls, the three objections an advisory group raises first */
s.addShape(pres.ShapeType.line, {
  x: CX + 0.22, y: 5.62, w: CW - 0.44, h: 0,
  line: { color: RULE, width: 0.75 },
});
s.addText("CONTROLS", {
  x: CX + 0.22, y: 5.70, w: CW - 0.44, h: 0.20, margin: 0,
  fontFace: SANS, fontSize: 9, bold: true, color: TEAL, charSpacing: 1.1,
});
s.addText(
  [
    { text: "Arousal matched", options: { bold: true, color: INK } },
    { text: ", stance still decoded within each level.", options: { color: MUTED, breakLine: true } },
    { text: "Speaker held out", options: { bold: true, color: INK } },
    { text: ", WavLM 0.573 to 0.530 by show.", options: { color: MUTED, breakLine: true } },
    { text: "Non-independence", options: { bold: true, color: INK } },
    { text: ", episode folds, bootstrap, 200 permutations.", options: { color: MUTED } },
  ],
  { x: CX + 0.22, y: 5.94, w: CW - 0.44, h: 0.46, margin: 0,
    fontFace: SANS, fontSize: 8.5, lineSpacingMultiple: 1.06 }
);

/* ---------------- right, the chart ---------------- */

const RX = 4.78, RW = 8.02;

s.addText("HOW WELL EACH REPRESENTATION RECOVERS SPEAKER STANCE", {
  x: RX, y: CY + 0.02, w: RW, h: 0.22, margin: 0,
  fontFace: SANS, fontSize: 9, bold: true, color: TEAL, charSpacing: 1.1,
});

const BAR_X = RX + 2.40;
const BAR_MAX = 4.55;
const SCALE_MAX = 0.62;
const ROW_TOP = 3.16;
const PITCH = 0.30;
const BAR_H = 0.215;

const rows = [
  ["WavLM", 0.573, TEAL, false],
  ["Whisper encoder", 0.564, TEAL, false],
  ["HuBERT", 0.520, TEAL, false],
  ["Text, word only", 0.487, GREY_BAR, false],
  ["Mimi, deployed tokeniser", 0.381, CLAY, true],
  ["Text, with context", 0.378, GREY_BAR, false],
];

[0, 0.2, 0.4, 0.6].forEach((v) => {
  const gx = BAR_X + (v / SCALE_MAX) * BAR_MAX;
  s.addShape(pres.ShapeType.line, {
    x: gx, y: ROW_TOP - 0.05, w: 0, h: PITCH * rows.length + 0.02,
    line: { color: v === 0 ? RULE : "EDEFF2", width: v === 0 ? 1 : 0.75 },
  });
  s.addText(v.toFixed(1), {
    x: gx - 0.25, y: ROW_TOP + PITCH * rows.length, w: 0.5, h: 0.20, margin: 0,
    fontFace: SANS, fontSize: 8.5, color: FAINT, align: "center",
  });
});

// chance line, the mean of the empirical permutation null
const CHANCE = 0.33;
const cx = BAR_X + (CHANCE / SCALE_MAX) * BAR_MAX;
s.addShape(pres.ShapeType.line, {
  x: cx, y: ROW_TOP - 0.08, w: 0, h: PITCH * rows.length + 0.04,
  line: { color: CLAY, width: 1.25, dashType: "dash" },
});
s.addText("chance, about 0.33", {
  x: cx - 1.05, y: ROW_TOP + PITCH * rows.length + 0.20, w: 2.10, h: 0.22, margin: 0,
  fontFace: SANS, fontSize: 8.5, italic: true, color: CLAY, align: "center",
});

rows.forEach(([label, val, colour, emph], i) => {
  const y = ROW_TOP + i * PITCH;
  s.addText(label, {
    x: RX, y: y - 0.02, w: 2.30, h: BAR_H + 0.04, margin: 0,
    fontFace: SANS, fontSize: 10, bold: !!emph,
    color: emph ? CLAY : INK, align: "right", valign: "middle",
  });
  s.addShape(pres.ShapeType.rect, {
    x: BAR_X, y: y, w: (val / SCALE_MAX) * BAR_MAX, h: BAR_H,
    fill: { color: colour }, line: { width: 0 },
  });
  s.addText(val.toFixed(3), {
    x: BAR_X + (val / SCALE_MAX) * BAR_MAX + 0.08, y: y - 0.02, w: 0.85, h: BAR_H + 0.04, margin: 0,
    fontFace: SANS, fontSize: 10, bold: true,
    color: emph ? CLAY : INK, valign: "middle",
  });
});

/* orientation, two halves. why-these-five also carries the colour key,
   since the model names are coloured to match their bars */
const HY = 5.44, HW = 3.90, HGAP = 0.22, HH = 1.00;

[0, 1].forEach((i) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: RX + i * (HW + HGAP), y: HY, w: HW, h: HH,
    fill: { color: "FFFFFF" }, line: { color: RULE, width: 0.75 }, rectRadius: 0.05,
  });
});

s.addText(
  [
    { text: "How to read this.  ", options: { bold: true, color: INK } },
    {
      text: "Each bar is how accurately a simple classifier recovers the speaker's stance (affiliative, neutral or adversarial) from that representation alone, scored by macro-F1. The dashed line is chance, the score the same probe reaches on shuffled labels, so the distance beyond it is the signal.",
      options: { color: MUTED },
    },
  ],
  { x: RX + 0.15, y: HY + 0.08, w: HW - 0.30, h: HH - 0.16, margin: 0,
    fontFace: SANS, fontSize: 9, lineSpacingMultiple: 1.06 }
);

const WX = RX + HW + HGAP;
s.addText(
  [
    { text: "Why these five.  ", options: { bold: true, color: INK } },
    { text: "Each pair isolates one variable. ", options: { color: MUTED } },
    { text: "WavLM", options: { bold: true, color: TEAL } },
    { text: " and ", options: { color: MUTED } },
    { text: "HuBERT", options: { bold: true, color: TEAL } },
    { text: " are both self-supervised, so no result rests on one model. ", options: { color: MUTED } },
    { text: "Whisper", options: { bold: true, color: TEAL } },
    { text: " is the same continuous form trained to transcribe, isolating what an ASR objective costs. ", options: { color: MUTED } },
    { text: "Mimi", options: { bold: true, color: CLAY } },
    { text: " has its first codebook distilled from WavLM, so quantisation is measured against its own teacher. ", options: { color: MUTED } },
    { text: "Text", options: { bold: true, color: "7C8896" } },
    { text: " appears twice, as a check and as the real baseline.", options: { color: MUTED } },
  ],
  { x: WX + 0.15, y: HY + 0.08, w: HW - 0.30, h: HH - 0.16, margin: 0,
    fontFace: SANS, fontSize: 9, lineSpacingMultiple: 1.06 }
);

/* ---------------- finding ---------------- */

const TY = 6.54;
s.addShape(pres.ShapeType.roundRect, {
  x: 0.5, y: TY, w: 12.3, h: 0.70,
  fill: { color: TEAL_TINT }, line: { color: "CBE0E2", width: 0.75 }, rectRadius: 0.06,
});
s.addText(
  [
    { text: "Finding.   ", options: { bold: true, color: TEAL } },
    {
      text: "Continuous representations preserve pragmatic stance, and it holds at matched arousal and on new speakers the probe never trained on, and within each word, where WavLM reaches 0.659 against 0.534 for text. The discrete tokens consumed by deployed systems sit barely above chance.",
      options: { color: INK },
    },
  ],
  { x: 0.72, y: TY + 0.10, w: 11.9, h: 0.52, margin: 0, fontFace: SANS, fontSize: 11.5, lineSpacingMultiple: 1.05 }
);

/* ---------------- speaker notes ---------------- */

s.addNotes(
`WHY THIS MATTERS
Systems such as Moshi convert speech into discrete tokens before any language model sees it, so whatever the tokeniser discards is unavailable downstream. If it discards pragmatic force, a system can recover every word correctly and still misread how the speaker meant them.

WHAT "PROBING" MEANS
The pretrained models are frozen, meaning never updated. We extract representations once and train only a small linear classifier on top, so any accuracy reflects what the representation already encodes rather than what a model learned for the task.

THE CORPUS BEHIND THE FUNNEL
The 7,310 hours is the full indexed collection, 6,281 episodes across 32 shows of political podcasts and broadcast programmes. It is the population sampled from rather than material analysed end to end, so describe it that way. The 873 keepers span 753 episodes and 32 shows. Candidates were drawn by a stratified pull balanced across shows and then topped up with sense-targeted and collocation-targeted pulls, because a purely random draw from a corpus this size over-samples the dominant sense of each word.

HUMAN PREMISE CHECK, RUN BEFORE ANY MODELLING
Two auxiliary annotators judged a counterbalanced 60-clip subset. Audio plus transcript reached 0.73 accuracy against 0.65 for transcript with discourse context, on a three-way chance of 0.33. So the contrast is partly text-recoverable but audio adds a real increment.

WHAT COUNTS AS CHANCE
Macro-F1 has no fixed chance value. A majority-class predictor scores only 0.196 here because macro-F1 gives zero to the two classes it never predicts, but our probe uses balanced class weights and spreads predictions across all three, so that is not its no-skill counterpart. The reference on the chart is the empirical permutation null, the same probe refit on shuffled labels, which sits near 0.33. Uniform and prior-matched random guessing give 0.322 and 0.333, agreeing closely.

ROBUSTNESS
Matched arousal. Stance is still decoded within each arousal level separately, so the probe is not simply reading loudness.
Speaker held out. Grouping folds by show rather than episode moves WavLM only from 0.573 to 0.530, so it is not riding speaker identity.
Non-independence. All scores are out of fold under GroupKFold by episode, with episode-cluster bootstrap intervals and 200-permutation tests. Every representation beats chance at p at most 0.01.

WHERE THE CONTRAST LIVES
WavLM peaks at layer 20 of 24 and falls away above it, consistent with upper layers shedding paralinguistics. Whisper plateaus across its top third. Inside Mimi, what little survives sits in codebook 0, the WavLM-distilled stream, at 0.402. The seven acoustic refinement codebooks are at or near chance and five of them are not significant. Chapter 2 predicted the opposite, so this is reported as a corrected expectation.

CAVEATS TO RAISE
The Mimi figure is all eight codebooks, the condition a deployed model actually consumes, at 0.381 against a chance of 0.311.
Pooled target-only text sits above chance only because the eight phrases differ in stance base rate, which is why the within-word figure is the clean lexical control.
Text with discourse context clears chance by only 0.045, close to Mimi, even though humans reached 0.65 from the same context. That gap is a limitation of the frozen sentence-embedding baseline rather than evidence that context is uninformative.
The training-free contrast-preservation score points the same way but is underpowered at 191 decisions and sensitive to the distance metric, so it is reported as corroborating only.`
);

pres.writeFile({ fileName: process.argv[2] || "advisory_slide.pptx" })
  .then(f => console.log("wrote", f));
