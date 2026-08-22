# Checkpoints

The exact model revisions that produced the reported figures, recorded from the local
Hugging Face cache before it was cleared.

This matters more here than in most studies. Chapter 4 argues that the loss is
architectural, and it reads frame rate, receptive field, latent width and encoder type
directly from these checkpoints. A model card that changes underneath the paper would
change the premises of that argument, so the revisions are pinned rather than left to
resolve to whatever `main` points at.

To fetch a pinned revision rather than the current one:

```python
from transformers import AutoModel
m = AutoModel.from_pretrained("microsoft/wavlm-large", revision="c1423ed94bb01d80a3f5ce5bc39f6026a0f4828c")
```

| Model | Revision | Role in the study |
|---|---|---|
| `microsoft/wavlm-large` | `c1423ed94bb01d80a3f5ce5bc39f6026a0f4828c` | continuous encoder, layer 20, the reference the ladder is read against |
| `facebook/hubert-large-ll60k` | `ff022d095678a2995f3c49bab18a96a9e553f782` | second continuous encoder, layer 23 |
| `openai/whisper-small` | `973afd24965f72e36ca33b3055d56a652f456b4d` | encoder layer 9, the control that shows the codec surplus is codec-specific |
| `kyutai/mimi` | `89091b3e466eb6a9d11e537bf26b144f194978f7` | hybrid codec, 8 attention layers, 178 ms receptive field, 512 latent |
| `descript/dac_24khz` | `6ba020b5ba7d9d8076fb90db7e67f27e31980f6e` | purely acoustic codec, no recurrence or attention, 221 ms, 1,024 latent |
| `facebook/encodec_24khz` | `c1dbe2ae3f1de713481a3b3e7c47f357092ee040` | recurrent codec, 113 ms, 128 latent, the middle rung of the architectural comparison |
| `cheoljun95/sylber` | `39451274641088bacc52c78a4bdc223086e6e92c` | variable-frame-rate, units derived from the signal |
| `lucadellalib/dycast` | `b81d1386ae048c8031610ae45813d2a18ef8ef97` | variable-frame-rate, units aligned to characters |
| `facebook/hubert-base-ls960` | `dba3bb02fda4248b6e082697eee756de8fe8aa8a` | config only, never used for extraction |

## Two entries that need explaining

WavLM and HuBERT each held two snapshot directories in the cache, which looks like two
competing weight revisions and is not. One directory held `model.safetensors` and the
other held `config.json` with `pytorch_model.bin`, so the library resolved different files
from different revisions of the same repository. The revision named above is what
`refs/main` pointed at, and it is the one carrying the config the architecture figures were
read from. The second hash is recorded here for completeness.

| Model | Second snapshot | Held |
|---|---|---|
| `microsoft/wavlm-large` | `07d9d3d8576fd3d718ee7b16b2b6242e9610d9af` | `model.safetensors` |
| `facebook/hubert-large-ll60k` | `1c513b9a0780f7afa32e4480311fa444e56c3a2e` | `model.safetensors` |

## Not part of the study

`facebook/mms-1b-all` was cached at 3.6 GB and is referenced nowhere in the code, the
drafts or the results. It is recorded here only so that a reader who finds it mentioned in
an old commit knows it was an abandoned line rather than an undocumented component.
