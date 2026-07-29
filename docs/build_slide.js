const pptxgen = require("pptxgenjs");

const INK = "131920";
const MUTED = "5C6773";
const FAINT = "8A94A1";
const TEAL = "0F7A84";
const TEAL_TINT = "EAF2F3";
const CLAY = "B4522F";
const CLAY_TINT = "F7EDE8";
const GREY_BAR = "94A0AE";
const PALE = "D5DAE0";
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
  x: 0.5, y: 0.28, w: 12.3, h: 0.6, margin: 0,
  fontFace: SERIF, fontSize: 27, bold: true, color: INK,
});

s.addText(
  "Deployed speech-to-speech systems never hear audio. They hear discrete tokens. Do those tokens still carry what a speaker meant?",
  {
    x: 0.5, y: 0.93, w: 12.3, h: 0.42, margin: 0,
    fontFace: SERIF, fontSize: 14.5, italic: true, color: TEAL,
  }
);

s.addText("MSc Computational Linguistics, UCL   |   Track A, Pragmatic Contrast Preservation   |   Advisory group, July 2026", {
  x: 0.5, y: 1.33, w: 12.3, h: 0.28, margin: 0,
  fontFace: SANS, fontSize: 10, color: FAINT, charSpacing: 0.6,
});

/* ---------------- left card, the design move ---------------- */

const CX = 0.5, CY = 1.78, CW = 4.05, CH = 4.40;

s.addShape(pres.ShapeType.roundRect, {
  x: CX, y: CY, w: CW, h: CH,
  fill: { color: CARD }, line: { color: RULE, width: 0.75 }, rectRadius: 0.06,
});

s.addText("THE DESIGN MOVE, LEXICAL CONTROL", {
  x: CX + 0.22, y: CY + 0.16, w: CW - 0.44, h: 0.24, margin: 0,
  fontFace: SANS, fontSize: 9.5, bold: true, color: TEAL, charSpacing: 1.1,
});

s.addText("yeah", {
  x: CX + 0.22, y: CY + 0.52, w: 1.5, h: 0.62, margin: 0,
  fontFace: SERIF, fontSize: 32, bold: true, color: TEAL, align: "center",
});
s.addText("vs", {
  x: CX + 1.72, y: CY + 0.70, w: 0.4, h: 0.3, margin: 0,
  fontFace: SANS, fontSize: 11, color: FAINT, align: "center",
});
s.addText("yeah", {
  x: CX + 2.12, y: CY + 0.52, w: 1.5, h: 0.62, margin: 0,
  fontFace: SERIF, fontSize: 32, bold: true, italic: true, color: CLAY, align: "center",
});

s.addText("SINCERE AGREEMENT", {
  x: CX + 0.10, y: CY + 1.14, w: 1.74, h: 0.22, margin: 0,
  fontFace: SANS, fontSize: 8.5, bold: true, color: MUTED, align: "center", charSpacing: 0.5,
});
s.addText("SARCASTIC DISMISSAL", {
  x: CX + 2.00, y: CY + 1.14, w: 1.74, h: 0.22, margin: 0,
  fontFace: SANS, fontSize: 8.5, bold: true, color: MUTED, align: "center", charSpacing: 0.5,
});

s.addText("Identical transcript. Opposite meaning.", {
  x: CX + 0.22, y: CY + 1.46, w: CW - 0.44, h: 0.26, margin: 0,
  fontFace: SERIF, fontSize: 12.5, italic: true, color: INK, align: "center",
});

s.addText(
  "Earlier work showed speech beats text on pragmatic tasks, but the utterances also differed in wording, so delivery stayed confounded with word choice. Holding the word constant removes that explanation. Whatever a probe recovers has to come from how it was said.",
  {
    x: CX + 0.22, y: CY + 1.82, w: CW - 0.44, h: 1.28, margin: 0,
    fontFace: SANS, fontSize: 11, color: MUTED, lineSpacingMultiple: 1.12,
  }
);

const facts = [
  ["873", "labelled clips"],
  ["8", "target phrases"],
  ["32", "shows, 753 episodes"],
];
facts.forEach(([n, k], i) => {
  const fx = CX + 0.22 + i * 1.22;
  s.addText(n, {
    x: fx, y: CY + 3.24, w: 1.18, h: 0.34, margin: 0,
    fontFace: SANS, fontSize: 19, bold: true, color: INK,
  });
  s.addText(k, {
    x: fx, y: CY + 3.58, w: 1.18, h: 0.46, margin: 0,
    fontFace: SANS, fontSize: 9, color: MUTED,
  });
});

/* ---------------- right, the chart ---------------- */

const RX = 4.78, RW = 8.02;

s.addText("HOW WELL EACH REPRESENTATION RECOVERS SPEAKER STANCE", {
  x: RX, y: CY + 0.02, w: RW, h: 0.24, margin: 0,
  fontFace: SANS, fontSize: 9.5, bold: true, color: TEAL, charSpacing: 1.1,
});

/* Bars are drawn as shapes rather than an embedded chart object. pptxgenjs
   emits an undeclared third axis id for this configuration, which makes
   PowerPoint discard the chart. Shapes render everywhere and stay editable. */

const BAR_X = RX + 2.40;      // where every bar starts
const BAR_MAX = 4.55;         // width representing SCALE_MAX
const SCALE_MAX = 0.62;
const ROW_TOP = CY + 0.36;
const PITCH = 0.335;
const BAR_H = 0.235;

const rows = [
  ["WavLM", 0.573, TEAL, false],
  ["Whisper encoder", 0.564, TEAL, false],
  ["HuBERT", 0.520, TEAL, false],
  ["Text, word only", 0.487, GREY_BAR, false],
  ["Text, with context", 0.378, GREY_BAR, false],
  ["Mimi, deployed tokeniser", 0.352, CLAY, true],
  ["No-skill baseline", 0.196, PALE, false],
];

// gridlines behind the bars
[0, 0.2, 0.4, 0.6].forEach((v) => {
  const gx = BAR_X + (v / SCALE_MAX) * BAR_MAX;
  s.addShape(pres.ShapeType.line, {
    x: gx, y: ROW_TOP - 0.05, w: 0, h: PITCH * rows.length + 0.02,
    line: { color: v === 0 ? RULE : "EDEFF2", width: v === 0 ? 1 : 0.75 },
  });
  s.addText(v.toFixed(1), {
    x: gx - 0.25, y: ROW_TOP + PITCH * rows.length + 0.00, w: 0.5, h: 0.22, margin: 0,
    fontFace: SANS, fontSize: 8.5, color: FAINT, align: "center",
  });
});

rows.forEach(([label, val, colour, emph], i) => {
  const y = ROW_TOP + i * PITCH;

  s.addText(label, {
    x: RX, y: y - 0.02, w: 2.30, h: BAR_H + 0.04, margin: 0,
    fontFace: SANS, fontSize: 10.5, bold: !!emph,
    color: emph ? CLAY : (val === 0.196 ? MUTED : INK),
    align: "right", valign: "middle",
  });

  // value bar
  s.addShape(pres.ShapeType.rect, {
    x: BAR_X, y: y, w: (val / SCALE_MAX) * BAR_MAX, h: BAR_H,
    fill: { color: colour }, line: { width: 0 },
  });

  s.addText(val.toFixed(3), {
    x: BAR_X + (val / SCALE_MAX) * BAR_MAX + 0.08, y: y - 0.02, w: 0.85, h: BAR_H + 0.04, margin: 0,
    fontFace: SANS, fontSize: 10.5, bold: true,
    color: emph ? CLAY : INK, valign: "middle",
  });
});


// how-to-read explainer
const HY = 4.85;
s.addShape(pres.ShapeType.roundRect, {
  x: RX, y: HY, w: RW, h: 0.88,
  fill: { color: "FFFFFF" }, line: { color: RULE, width: 0.75 }, rectRadius: 0.05,
});
s.addText(
  [
    { text: "How to read this.   ", options: { bold: true, color: INK } },
    {
      text: "Each bar is how accurately a simple classifier recovers the speaker's stance (affiliative, neutral or adversarial) from that representation alone, scored by macro-F1. Higher means more of the meaning survived. The pale bar is what a model with no real skill scores, so the distance above it is the signal.",
      options: { color: MUTED },
    },
  ],
  {
    x: RX + 0.16, y: HY + 0.09, w: RW - 0.32, h: 0.70, margin: 0,
    fontFace: SANS, fontSize: 10.5, lineSpacingMultiple: 1.1,
  }
);

// the within-word control, the key caveat line
s.addText(
  [
    { text: "Word held constant.   ", options: { bold: true, color: INK } },
    {
      text: "Averaged within each of the eight phrases, WavLM scores 0.659 against 0.534 for text, so the contrast survives even when the word itself cannot help.",
      options: { color: MUTED },
    },
  ],
  {
    x: RX, y: HY + 0.98, w: RW, h: 0.36, margin: 0,
    fontFace: SANS, fontSize: 10.5,
  }
);

/* ---------------- bottom takeaway ---------------- */

const TY = 6.32;
s.addShape(pres.ShapeType.roundRect, {
  x: 0.5, y: TY, w: 12.3, h: 0.72,
  fill: { color: TEAL_TINT }, line: { color: "CBE0E2", width: 0.75 }, rectRadius: 0.06,
});
s.addText(
  [
    { text: "Finding.   ", options: { bold: true, color: TEAL, fontFace: SANS } },
    {
      text: "Continuous representations preserve pragmatic stance, and it holds at matched arousal and on speakers the probe never trained on. The discrete tokens deployed systems actually consume lose most of it, though not all.",
      options: { color: INK, fontFace: SANS },
    },
  ],
  {
    x: 0.72, y: TY + 0.13, w: 11.9, h: 0.48, margin: 0,
    fontSize: 12,
  }
);

/* ---------------- speaker notes ---------------- */

s.addNotes(
`WHY THIS MATTERS
Systems such as Moshi convert speech into discrete tokens before any language model sees it, so whatever the tokeniser discards is unavailable downstream. If it discards pragmatic force, a system can recover every word correctly and still misread how the speaker meant them.

WHAT "PROBING" MEANS
The pretrained models are frozen, meaning never updated. We extract representations once and train only a small linear classifier on top, so any accuracy reflects what the representation already encodes rather than what a model learned for the task.

DATA
873 labelled clips across eight phrases (yeah, okay, right, sure, great, fine, really, come on), 753 episodes, 32 shows. Naturalistic political podcast audio rather than acted emotion corpora. Stance and arousal were labelled on independent axes so the arousal confound could be tested directly.

HUMAN PREMISE CHECK, RUN BEFORE ANY MODELLING
Two auxiliary annotators judged a counterbalanced 60-clip subset. Audio plus transcript reached 0.73 accuracy against 0.65 for transcript with discourse context, on a three-way chance of 0.33. So the contrast is partly text-recoverable but audio adds a real increment.

ROBUSTNESS
Matched arousal. Stance is still decoded within each arousal level separately, so the probe is not simply reading loudness.
Speaker held out. Grouping folds by show rather than episode moves WavLM only from 0.573 to 0.530, so it is not riding speaker identity.
Non-independence. All scores are out of fold under GroupKFold by episode, with episode-cluster bootstrap intervals and 200-permutation tests. Every representation beats chance at p at most 0.01.

WHERE THE CONTRAST LIVES
WavLM peaks at layer 20 of 24 and falls away above it, consistent with upper layers shedding paralinguistics. Whisper plateaus across its top third. Inside Mimi the loss is not localised, since refinement codebooks 1 to 7 each score between 0.33 and 0.37 and stacking them adds nothing.

CAVEATS TO RAISE
Pooled target-only text sits above chance only because the eight phrases differ in stance base rate, which is why the within-word figure is the clean lexical control.
Mimi is significantly above chance, so the honest claim is that default tokenisation loses most of the contrast, not all of it. The loss is recoverable with deliberate effort, but deployed systems use the defaults.
The training-free contrast-preservation score points the same way but is underpowered at 191 decisions and sensitive to the distance metric, so it is reported as corroborating only.

NEXT
Probe Mimi codebook 0, the WavLM-distilled stream, which was not extracted in the first run. It is the one remaining untested possibility for where pragmatic information might survive inside the tokeniser.`
);

pres.writeFile({ fileName: "/private/tmp/claude-501/-Users-carolineswartz-Desktop-Parallel-Frontier/cc920fb3-402b-4409-b43b-d506417adb91/scratchpad/advisory_slide.pptx" })
  .then(f => console.log("wrote", f));
