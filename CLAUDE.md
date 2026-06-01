# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## Overview

This is a fork of **official YOLOv7** ([WongKinYiu/yolov7](https://github.com/WongKinYiu/yolov7))
adapted to train a **5-class tongue-diagnosis (舌診) object detector**. The trained model is
intended for deployment on the **AMB82 / AMB82-MINI** Realtek AIoT board (Arduino-compatible,
with an on-board NPU), so the export/conversion workflow (PyTorch → ONNX) matters as much as
training accuracy.

The 5 tongue-coating classes (`data/tongue_v7.yaml`):

```
Mirror-Approximated, Thin-White, White-Greasy, Yellow-Greasy, Grey-Black
```

> Note: `README.md` is still the **unmodified upstream YOLOv7 README** — treat it as YOLOv7
> reference material, not as documentation of this project. This file is the project-specific
> source of truth.

## Project-specific vs. upstream

**Almost all code is stock YOLOv7.** Do not assume a file is custom just because it is here.
The pieces actually specific to this project are:

- `data/tongue_v7.yaml` — the 5-class dataset config (the real one).
- `tongue_model.zip` (~20 MB) — the trained checkpoint + conversion progress; this is the
  project deliverable.
- A handful of one-off helper scripts at the repo root (see below).
- The ONNX export workflow used to convert weights for the AMB82 NPU.

Everything in `models/`, `utils/`, `cfg/`, `tools/`, `deploy/`, and the main `train.py` /
`test.py` / `detect.py` / `export.py` scripts is inherited YOLOv7 — when changing them, prefer
minimal, upstream-compatible edits.

## Repository structure

```
train.py            # Main training loop (P5 models, 640px). Default --data is coco.yaml — override it.
train_aux.py        # Training for larger P6 / aux-head models (1280px: w6/e6/e6e/d6).
test.py             # Evaluation: mAP / precision / recall, confusion matrix.
detect.py           # Inference on image / folder / video / webcam.
export.py           # Export weights to TorchScript / ONNX / CoreML (ONNX path feeds AMB82).
hubconf.py          # torch.hub entry points.
reparam_yolov7-tiny.py  # Reparameterize a trained yolov7-tiny into deploy form.

models/             # yolo.py (Detect/IDetect heads), common.py (layers), experimental.py
utils/              # datasets.py, loss.py, general.py (NMS, coords), metrics.py, plots.py, torch_utils.py
cfg/training/       # Model architecture YAMLs for TRAINING (yolov7, -tiny, x, w6, e6, e6e, d6)
cfg/deploy/         # Same models in DEPLOY form (used after reparameterization)
cfg/baseline/       # Baseline reference configs
data/               # tongue_v7.yaml (custom), coco.yaml, hyp.scratch.*.yaml hyperparameters
tools/              # Export/visualization Jupyter notebooks (ONNX, TensorRT, CoreML, etc.)
deploy/triton-inference-server/  # NVIDIA Triton serving example (upstream)
inference/images/   # Sample images for detect.py
```

## Common commands

Setup:
```bash
pip install -r requirements.txt
```

Train (640px, single GPU). Always pass `--data data/tongue_v7.yaml`:
```bash
python train.py --data data/tongue_v7.yaml --cfg cfg/training/yolov7.yaml \
  --weights yolov7.pt --hyp data/hyp.scratch.custom.yaml \
  --img 640 640 --batch-size 16 --epochs 300 --device 0
```
(For w6/e6/e6e/d6 use `train_aux.py` with the matching `cfg/training/*.yaml` and `--img 1280 1280`.)

Evaluate:
```bash
python test.py --data data/tongue_v7.yaml --weights runs/train/exp/weights/best.pt --img 640
```

Inference:
```bash
python detect.py --weights runs/train/exp/weights/best.pt --source inference/images --img 640 --conf-thres 0.25
```

Reparameterize a trained tiny model (training graph → deploy graph) before export:
```bash
python reparam_yolov7-tiny.py
```

Export to ONNX (the format consumed by the AMB82 toolchain):
```bash
python export.py --weights best.pt --img-size 640 640 --grid --end2end --simplify --max-wh 640
```
ONNX export requires the (commented-out) export extras — install as needed:
`pip install onnx onnx-simplifier`.

## Conventions & gotchas

- **Python ≥ 3.7, PyTorch ≥ 1.7.** Note the strict pins in `requirements.txt`: `numpy<1.24`,
  `protobuf<4.21.3`, and excluded torch/torchvision versions (`!=1.12.0`, `!=0.13.0`). Don't
  loosen these casually.
- **Dataset is external / not committed.** `data/tongue_v7.yaml` expects YOLO-format data at
  `./data/images/{train,val}` with labels under `./data/labels/{train,val}`. Use `auto_split.py`
  to split a flat `images/JPEGImages` + `labels` set into train/val.
- **Outputs** land in `runs/train/expN/`, `runs/test/`, `runs/detect/` (gitignored). Best/last
  checkpoints are at `runs/train/expN/weights/{best,last}.pt`.
- **Helper scripts at root are one-off patches, not part of the pipeline:**
  - `make_yaml.py` — regenerates `data/tongue_v7.yaml`.
  - `auto_split.py` — splits the dataset into train/val.
  - `fix_load.py` — patches `train.py`/`detect.py` to add `weights_only=False` to `torch.load`
    (needed for newer PyTorch checkpoint security). `fix_test.py` does the same for `test.py`;
    `undo_fix.py` reverts. These mutate source files in place — be aware before re-running.
- The canonical dataset config is `data/tongue_v7.yaml` — this is the file the scripts
  reference. (A stray `tongue_v7.yaml.yaml` duplicate previously existed and was removed.)
- Several source files and notebooks contain **Traditional Chinese (zh-TW) comments** — preserve
  them when editing.
- **License: GPLv3** (`LICENSE.md`, inherited from YOLOv7).

## Git workflow

- Default branch: `main`. Active development branch for this work: `claude/claude-md-docs-i3ymp`.
- Develop on the designated feature branch, commit with clear messages, and push with
  `git push -u origin <branch>`. Do not push to `main` without explicit permission, and do not
  open a PR unless asked.
- Avoid committing large binaries/artifacts beyond the existing `tongue_model.zip`; checkpoints
  and `runs/` are gitignored for a reason.
