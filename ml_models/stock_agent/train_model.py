import json
import math
import os

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "src", "main", "java", "vn", "ptit", "aistudio", "dto", "chung_khoan", "Chung_khoan.csv")
METRICS_PATH = os.path.join(SCRIPT_DIR, "metrics.json")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def calc_naive_metrics(df):
  split = int(len(df) * 0.8)
  test = df.iloc[split:].copy()
  actual = test["Close"].astype(float)
  pred = df["Close"].shift(1).iloc[split:].astype(float)
  err = actual - pred
  rmse = math.sqrt(float((err ** 2).mean()))
  mae = float(err.abs().mean())
  mape = float((err.abs() / actual).mean() * 100)
  actual_dir = actual.diff().fillna(0) >= 0
  pred_dir = pred.diff().fillna(0) >= 0
  da = float((actual_dir == pred_dir).mean())
  return {"rmse": round(rmse, 2), "mae": round(mae, 2), "mape": round(mape, 2), "directional_accuracy": round(da, 3)}


def main():
  df = pd.read_csv(CSV_PATH).sort_values("Date")
  naive = calc_naive_metrics(df)
  metrics = {
    "as_of_date": str(df["Date"].iloc[-1]),
    "models": {
      "lstm_demo": {**naive, "note": "Scaffold only: replace with trained LSTM metrics after adding TensorFlow/PyTorch."},
      "gru_demo": {**naive, "note": "Scaffold only: replace with trained GRU metrics after adding TensorFlow/PyTorch."},
      "naive_persistence": {**naive, "note": "Computed by train_model.py: next price equals previous close."}
    }
  }
  config = {
    "ticker": "AMZN",
    "target": "next_log_return",
    "window": 30,
    "split": "time_ordered_70_10_20",
    "features": ["log_return", "range_ratio", "log_volume_change", "ma5_ratio", "ma20_ratio", "volatility10", "rsi14"],
    "note": "This scaffold writes baseline metrics; add a real LSTM/GRU stack for final training."
  }
  with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
  with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
  print(json.dumps({"metrics": metrics, "config": config}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
