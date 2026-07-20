# The whole project, explained like you're 10

This is a plain-language tour of what the dissertation asks, everything we've built so far,
and how the final paper is laid out. No jargon. If you can follow this, you understand the
project.

## The big question

People can say the exact same word and mean opposite things, just by how they say it.
"Yeah" can mean "yes, totally!" or a sarcastic "yeah, riiight." Same word. Opposite feeling.
The feeling is carried by the *voice*, not the letters.

The question of this whole project is simple:

> When computers listen to speech, do they keep that feeling? Or do they only catch the word
> and throw the feeling away?

## Why anyone should care

More and more, we talk to computers and they talk back (think of a voice assistant that
answers out loud). To do that, they squish speech down into a small code so it's cheap and
fast to handle. If that squishing throws away the *feeling* in a voice, then these systems
might hear a sarcastic "great" and a delighted "great" as the same thing. That would mean
they miss how people actually feel, which matters a lot for polite, safe, honest machines.

## What we collected

We used real audio from political podcasts (real people talking naturally, not actors
pretending). We hunted for eight little words that flip meaning depending on delivery:
**yeah, okay, right, sure, great, fine, really, come on.** We ended up with **873 clips**,
each one a moment where someone says one of those words.

## Putting feeling-labels on them

A human (that's the researcher) listened to each clip and tagged it with the feeling behind
it, using three simple buckets:
- **Friendly** (warm, agreeing)
- **In-between** (just acknowledging)
- **Against** (sarcastic, dismissive, hostile)

We also wrote down whether the voice was **calm or excited** (loudness/energy), kept
*separately* from the feeling, because those are two different things. That separation
becomes important later.

## First, a sanity check (the "premise check")

Before trusting any computer, we checked something with *people*: can a human hear the
feeling from the audio, but NOT guess it from the plain written words alone? We gave two
helpers the same clips two ways: once as just text, once with the sound. They did better
*with* the sound (about 73 out of 100 right) than with text alone (about 65 out of 100).
Guessing blindly would be about 33. So yes, the feeling really does live in the *voice*.
Good. We were allowed to keep going.

## The big-computer day (turning sound into numbers)

To test the computers, we used five different "listening robots." Each one hears a clip and
turns it into a long list of numbers, like a fingerprint of what it noticed:
- **WavLM** and **HuBERT**: really good ears, notice tiny details of *how* a voice sounds.
- **Whisper**: an ear that's used to turning speech into written words.
- **Mimi**: the special one. It's the kind of squished-down code that real talking-robots
  actually use. Think of shrinking a photo so small you can text it easily, but it gets a
  bit blurry.
- **Text**: not listening at all, just reading the written word. Our "what if you only had
  subtitles?" comparison.

These robots are heavy, so we *rented* a powerful faraway computer with a fast chip (a GPU)
for about ten minutes, ran all the clips through the five robots, saved the number-
fingerprints, brought them home, and gave the rented computer back so we stopped paying.

## The quiz (the "probe")

Then we played a fair guessing game on our own laptop. We covered up the answers and asked a
simple little quiz-taker: "Just from these numbers, can you tell if this word was Friendly,
In-between, or Against?" We were strict about fairness: the quiz-taker was never allowed to
study clips from a show and then be tested on that same show, so it couldn't cheat.

## What we found (the exciting part)

- The good-ears robots (WavLM, Whisper, HuBERT) guessed the feeling clearly better than
  random. The feeling really is in the sound, and they keep it.
- **Mimi did much worse.** The squished-down code that real talking-robots use **loses most
  of the feeling.** The word survives; the feeling goes blurry.
- Reading subtitles only was so-so, which makes sense.

And we numbered-checked it: these results are very unlikely to be luck.

## The careful "are you sure?" checks

Good science pokes its own findings to see if they fall over. We poked three ways:
1. **Is it just loudness?** We re-checked with calm and excited clips kept apart. The robots
   still heard the feeling, so it's not just "loud = angry."
2. **Is it just recognizing the person?** We re-checked so the quiz-taker was tested on
   people it had never studied. It still worked. So it's reading the *feeling*, not the
   speaker.
3. **A no-training test (called CPS).** A very strict extra check. It pointed the same way
   (real audio best, Mimi worst) but it was **wobbly** because we only had a few clips that
   fit its strict rules. So we report it honestly as "agrees, but weak," and we don't lean on
   it. The strong checks above carry the argument.

## The one-sentence result

**Real, un-squished audio keeps the feeling in people's voices; the squished code that
talking-robots actually use loses most of it, even when it gets the words right.**

---

# How the written paper is laid out

The final paper can be at most 10,000 words (about 30-ish pages). Think of it as six
chapters, like chapters of a story:

1. **Introduction** — "Here's the puzzle and why it matters." (the yeah/riiight idea, and
   the talking-robots angle)
2. **What others already found** — "Here's what smart people discovered before me, and the
   one question they left open." (nobody kept the word the same while changing the feeling)
3. **How I did it** — "Here are my clips, my feeling-labels, my five robots, and my fair
   quiz." (the recipe, so anyone could repeat it)
4. **What I found** — "Here are the scores." (the tables: audio keeps the feeling, Mimi
   loses it)
5. **What it means** — "Here's why these scores matter for real talking-robots."
6. **Wrapping up** — "Here's the short version, what my study couldn't do (the wobbly test),
   and what someone should try next."

Plus a short summary at the very top (the **abstract**), a list of all the books and papers
I used (the **references**), and extra detail at the back for anyone who wants to check my
work (the **appendices**: the exact labels, counts, and full score tables).

The trickiest part of the writing is Chapter 2: I've written a lot and now have to make it
much shorter to fit the word limit. Everything else has enough room.
