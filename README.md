# AMB82 舌苔辨識 (Tongue-Coating Detection)

基於 **YOLOv7** 訓練的 **5 類舌苔（舌診 / 舌象）物件偵測模型**，
最終目標是部署到 **AMB82 / AMB82-MINI**（Realtek 的 Arduino 相容 AIoT 開發板，
內建 NPU），因此 **PyTorch → ONNX 的轉檔流程** 與訓練準確度同等重要。

> 本專案 fork 自官方 YOLOv7（[WongKinYiu/yolov7](https://github.com/WongKinYiu/yolov7)），
> 並在其上加入舌苔資料集設定與訓練/轉檔成果。授權沿用上游的 **GPLv3**（見 `LICENSE.md`）。

## 偵測類別

`data/tongue_v7.yaml` 定義 5 類舌苔：

```
Mirror-Approximated, Thin-White, White-Greasy, Yellow-Greasy, Grey-Black
```

## 專案結構

```
train.py            # 主訓練流程（P5 模型，640px）。預設 --data 是 coco.yaml，務必覆蓋。
train_aux.py        # 較大 P6 / aux-head 模型訓練（1280px：w6/e6/e6e/d6）。
test.py             # 評估：mAP / precision / recall、混淆矩陣。
detect.py           # 推論（圖片 / 資料夾 / 影片 / webcam）。
export.py           # 匯出權重至 TorchScript / ONNX / CoreML（ONNX 路徑供 AMB82 使用）。
reparam_yolov7-tiny.py  # 將訓練好的 yolov7-tiny 重參數化成 deploy 形式。

models/             # yolo.py（Detect/IDetect head）、common.py（layers）、experimental.py
utils/              # datasets.py、loss.py、general.py、metrics.py、plots.py、torch_utils.py
cfg/training/       # 訓練用模型架構 YAML（yolov7、-tiny、x、w6、e6、e6e、d6）
cfg/deploy/         # 同模型的 deploy 形式（重參數化後使用）
data/               # tongue_v7.yaml（本專案）、hyp.scratch.*.yaml 超參數
tools/              # 匯出 notebook：YOLOv7onnx、YOLOv7trt、reparameterization
tongue_model.zip    # 訓練成果：重參數化後的 best_reparam.onnx + yolov7_tiny.json
```

> 註：`README.md` 以外的程式碼幾乎都是上游 YOLOv7 原始碼。本專案真正客製的部分只有
> `data/tongue_v7.yaml`、`tongue_model.zip` 與供 AMB82 使用的 ONNX 轉檔流程。

## 環境安裝

需求：Python ≥ 3.7、PyTorch ≥ 1.7。注意 `requirements.txt` 的版本鎖定
（`numpy<1.24`、`protobuf<4.21.3`，以及排除的 torch/torchvision 版本），請勿隨意放寬。

```bash
pip install -r requirements.txt
```

## 常用指令

訓練（640px，單 GPU）。請務必帶上 `--data data/tongue_v7.yaml`：

```bash
python train.py --data data/tongue_v7.yaml --cfg cfg/training/yolov7.yaml \
  --weights yolov7.pt --hyp data/hyp.scratch.custom.yaml \
  --img 640 640 --batch-size 16 --epochs 300 --device 0
```

評估：

```bash
python test.py --data data/tongue_v7.yaml --weights runs/train/exp/weights/best.pt --img 640
```

推論：

```bash
python detect.py --weights runs/train/exp/weights/best.pt --source <圖片/資料夾/影片> --img 640 --conf-thres 0.25
```

重參數化 tiny 模型（訓練圖 → deploy 圖），匯出前先執行：

```bash
python reparam_yolov7-tiny.py
```

匯出 ONNX（AMB82 工具鏈使用的格式）：

```bash
python export.py --weights best.pt --img-size 640 640 --grid --end2end --simplify --max-wh 640
```

ONNX 匯出需額外安裝：`pip install onnx onnx-simplifier`。

## 資料集

資料集為外部資料、未納入版控。`data/tongue_v7.yaml` 預期 YOLO 格式資料位於
`./data/images/{train,val}`，標註位於 `./data/labels/{train,val}`。可用
`auto_split.py` 將扁平的 `images/JPEGImages` + `labels` 切成 train/val。

## 一次性輔助腳本（根目錄）

- `make_yaml.py` — 重新產生 `data/tongue_v7.yaml`。
- `auto_split.py` — 切分 train/val。
- `fix_load.py` / `fix_test.py` — 在 `train.py`/`detect.py`/`test.py` 的 `torch.load`
  加上 `weights_only=False`（新版 PyTorch 載入安全限制）；`undo_fix.py` 還原。
  這些會就地改動原始碼，重跑前請留意。

更完整的開發說明見 `CLAUDE.md`。
