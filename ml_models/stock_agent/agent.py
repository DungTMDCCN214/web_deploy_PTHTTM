import csv
import json
import math
import os
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8")

try:
  import pandas as pd
except Exception as exc:
  pd = None
  PANDAS_ERROR = str(exc)
else:
  PANDAS_ERROR = None

try:
  from sklearn.feature_extraction.text import TfidfVectorizer
  from sklearn.metrics.pairwise import cosine_similarity
except Exception:
  TfidfVectorizer = None
  cosine_similarity = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "src", "main", "java", "vn", "ptit", "aistudio", "dto", "chung_khoan", "Chung_khoan.csv")
KG_PATH = os.path.join(SCRIPT_DIR, "kg_triples.csv")
DOCS_PATH = os.path.join(SCRIPT_DIR, "docs.json")
METRICS_PATH = os.path.join(SCRIPT_DIR, "metrics.json")
AS_OF_DATE = "2020-09-23"
DISCLAIMER = "Kết quả chỉ phục vụ học tập, không phải tư vấn đầu tư."

_PRICE_DF = None
_TRIPLES = None
_DOCS = None
_METRICS = None


def read_input():
  raw = sys.stdin.read()
  if not raw and len(sys.argv) > 1:
    raw = sys.argv[1]
  return json.loads(raw or "{}")


def load_prices():
  global _PRICE_DF
  if _PRICE_DF is not None:
    return _PRICE_DF
  if pd is None:
    raise RuntimeError(f"Không nạp được pandas: {PANDAS_ERROR}")
  df = pd.read_csv(CSV_PATH)
  df["Date"] = pd.to_datetime(df["Date"])
  df = df.sort_values("Date").drop_duplicates("Date")
  for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
  df = df.dropna()
  _PRICE_DF = df
  return _PRICE_DF


def load_triples():
  global _TRIPLES
  if _TRIPLES is not None:
    return _TRIPLES
  triples = []
  with open(KG_PATH, encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
      triples.append((row["subject"], row["relation"], row["object"]))
  _TRIPLES = triples
  return triples


def load_docs():
  global _DOCS
  if _DOCS is not None:
    return _DOCS
  with open(DOCS_PATH, encoding="utf-8") as f:
    _DOCS = json.load(f)
  return _DOCS


def load_metrics():
  global _METRICS
  if _METRICS is not None:
    return _METRICS
  with open(METRICS_PATH, encoding="utf-8") as f:
    _METRICS = json.load(f)
  return _METRICS


def next_trading_days(as_of_date, horizon):
  current = datetime.strptime(as_of_date, "%Y-%m-%d")
  days = []
  while len(days) < horizon:
    current += timedelta(days=1)
    if current.weekday() < 5:
      days.append(current.strftime("%Y-%m-%d"))
  return days


def clip_as_of(as_of_date):
  df = load_prices()
  requested = pd.to_datetime(as_of_date or AS_OF_DATE)
  min_date = df["Date"].min()
  max_date = df["Date"].max()
  requested = max(min_date, min(max_date, requested))
  return requested.strftime("%Y-%m-%d")


def forecast_tool(as_of_date=AS_OF_DATE, horizon=5):
  df = load_prices()
  horizon = max(1, min(int(horizon or 5), 20))
  as_of_date = clip_as_of(as_of_date)
  hist = df[df["Date"] <= pd.to_datetime(as_of_date)].copy()
  if len(hist) < 60:
    raise ValueError("Không đủ dữ liệu lịch sử để dự báo.")

  closes = hist["Close"].astype(float)
  log_returns = (closes / closes.shift(1)).apply(lambda x: math.log(x) if x > 0 else 0).dropna()
  recent = log_returns.tail(30)
  drift = float(recent.mean())
  sigma = float(recent.std() or log_returns.std() or 0.0)
  last_close = float(closes.iloc[-1])

  prices = []
  cumulative = 0.0
  for step, date in enumerate(next_trading_days(as_of_date, horizon), start=1):
    cumulative += drift
    price = last_close * math.exp(cumulative)
    band = 1.96 * sigma * math.sqrt(step)
    lower = last_close * math.exp(cumulative - band)
    upper = last_close * math.exp(cumulative + band)
    prices.append({
      "date": date,
      "forecast_close": round(price, 2),
      "lower": round(lower, 2),
      "upper": round(upper, 2),
    })

  direction = "tăng" if prices[-1]["forecast_close"] > last_close else "giảm"
  return {
    "as_of_date": as_of_date,
    "horizon": horizon,
    "last_close": round(last_close, 2),
    "forecast": prices,
    "method": "rolling_log_return_demo",
    "direction": direction,
    "uncertainty_note": "Vùng bất định dùng độ lệch chuẩn log-return 30 phiên gần nhất; đây là demo, chưa phải LSTM thật.",
    "metrics": load_metrics(),
  }


def price_series(start=None, end=None):
  df = load_prices()
  if start:
    df = df[df["Date"] >= pd.to_datetime(start)]
  if end:
    df = df[df["Date"] <= pd.to_datetime(end)]
  if len(df) > 260:
    df = df.tail(260)
  rows = []
  for _, row in df.iterrows():
    rows.append({
      "date": row["Date"].strftime("%Y-%m-%d"),
      "open": round(float(row["Open"]), 2),
      "high": round(float(row["High"]), 2),
      "low": round(float(row["Low"]), 2),
      "close": round(float(row["Close"]), 2),
      "volume": int(row["Volume"]),
    })
  return {"prices": rows, "count": len(rows), "as_of_date": AS_OF_DATE}


def detect_entities(question):
  q = (question or "").lower()
  aliases = {
    "Amazon": ["amazon", "amzn"],
    "AWS": ["aws", "cloud", "đám mây", "dam may"],
    "E_Commerce": ["e-commerce", "retail", "bán lẻ", "ban le", "thương mại điện tử"],
    "Federal_Reserve": ["fed", "federal reserve", "lãi suất", "lai suat", "interest"],
    "COVID19": ["covid", "pandemic", "dịch", "dich"],
    "Stock_Price": ["stock", "price", "giá", "gia", "cổ phiếu", "co phieu"],
  }
  seeds = []
  for entity, words in aliases.items():
    if any(word in q for word in words):
      seeds.append(entity)
  return seeds or ["Amazon"]


def kg_tool(question):
  triples = load_triples()
  seeds = detect_entities(question)
  adjacency = defaultdict(list)
  for s, r, o in triples:
    adjacency[s].append((s, r, o))
    adjacency[o].append((s, r, o))

  facts = []
  seen_facts = set()
  seen_nodes = set(seeds)
  queue = deque((seed, 0) for seed in seeds)
  while queue:
    node, depth = queue.popleft()
    if depth >= 2:
      continue
    for fact in adjacency.get(node, []):
      if fact not in seen_facts:
        seen_facts.add(fact)
        facts.append(list(fact))
      for candidate in (fact[0], fact[2]):
        if candidate not in seen_nodes:
          seen_nodes.add(candidate)
          queue.append((candidate, depth + 1))
  return {"seeds": seeds, "facts": facts[:16]}


def fallback_score(query, text):
  q_terms = set(query.lower().split())
  t_terms = set(text.lower().split())
  if not q_terms or not t_terms:
    return 0.0
  return len(q_terms & t_terms) / math.sqrt(len(q_terms) * len(t_terms))


def rag_tool(question, as_of_date=AS_OF_DATE, top_k=4):
  docs = [d for d in load_docs() if d["date"] <= (as_of_date or AS_OF_DATE)]
  if not docs:
    return []
  query = question or "Amazon AWS cloud revenue stock price"
  if TfidfVectorizer and cosine_similarity:
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([d["text"] + " " + d["section"] for d in docs])
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
  else:
    scores = [fallback_score(query, d["text"] + " " + d["section"]) for d in docs]
  ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:top_k]
  hits = []
  for idx, score in ranked:
    if float(score) <= 0.01:
      continue
    doc = docs[idx]
    hits.append({
      "id": doc["id"],
      "source": doc["source"],
      "doc_type": doc["doc_type"],
      "date": doc["date"],
      "page": doc["page"],
      "section": doc["section"],
      "text": doc["text"],
      "score": round(float(score), 4),
    })
  return hits


def is_in_scope(question):
  q = (question or "").lower()
  keywords = ["amazon", "amzn", "aws", "stock", "cổ phiếu", "co phieu", "giá", "gia", "forecast", "dự báo", "du bao", "cloud", "lãi suất", "lai suat"]
  return any(k in q for k in keywords)


def build_report(question, forecast, kg, hits, out_of_scope=False):
  if out_of_scope:
    return {
      "summary": "Không đủ thông tin trong phạm vi demo AMZN để trả lời câu hỏi này.",
      "sections": [
        "Câu hỏi nằm ngoài phạm vi tác tử tài chính AMZN.",
        "Không gọi công cụ dự báo/tri thức để tránh suy diễn.",
        DISCLAIMER,
      ],
      "disclaimer": DISCLAIMER,
    }

  evidence = "; ".join([f"{h['source']} · trang {h['page']} · {h['date']}" for h in hits]) or "Cơ sở tri thức không có đủ thông tin."
  facts = "; ".join([f"({s}, {r}, {o})" for s, r, o in kg["facts"][:5]]) or "Không có fact KG phù hợp."
  last = forecast["last_close"]
  final = forecast["forecast"][-1]["forecast_close"]
  direction = forecast["direction"]
  rmse = forecast["metrics"]["models"]["naive_persistence"]["rmse"]
  return {
    "summary": f"AMZN đóng cửa {last:.2f} USD tại {forecast['as_of_date']}; dự báo demo sau {forecast['horizon']} phiên là {final:.2f} USD, xu hướng {direction}.",
    "sections": [
      f"Tóm tắt kỹ thuật: Model Tool dùng log-return rolling, giá cuối {last:.2f} USD, dự báo 5 phiên kèm vùng bất định; baseline naive RMSE tham chiếu {rmse:.2f}.",
      f"Động lực cơ bản theo KG: {facts}",
      f"Bằng chứng RAG: {evidence}",
      "Rủi ro và bất định: dự báo chuỗi giá ngắn hạn rất nhạy với biến động thị trường; vùng bất định chỉ là xấp xỉ từ log-return gần đây.",
      "Giới hạn mô hình: bản demo hiện dùng Forecast Tool nhẹ thay cho LSTM/GRU thật; cần chạy train_model.py và thay model trước khi báo cáo chính thức.",
    ],
    "disclaimer": DISCLAIMER,
  }


def trace_step(tool, status, start, detail):
  return {
    "tool": tool,
    "status": status,
    "elapsed_ms": int((time.time() - start) * 1000),
    "detail": detail,
  }


def ask_agent(payload):
  question = payload.get("question", "")
  as_of_date = clip_as_of(payload.get("as_of_date") or AS_OF_DATE)
  horizon = payload.get("horizon", 5)
  trace = []
  plan = []

  started = time.time()
  in_scope = is_in_scope(question)
  plan.append("Observe: đọc câu hỏi và xác định phạm vi AMZN.")
  trace.append(trace_step("Router", "ok", started, "in_scope=" + str(in_scope)))

  if not in_scope:
    report = build_report(question, None, {"facts": []}, [], out_of_scope=True)
    return {
      "plan": plan + ["Reason: câu hỏi ngoài phạm vi.", "Act: trả lời không đủ thông tin."],
      "tool_calls": trace,
      "forecast": None,
      "kg_facts": [],
      "rag_hits": [],
      "report": report,
      "trace": trace,
      "disclaimer": DISCLAIMER,
    }

  started = time.time()
  forecast = forecast_tool(as_of_date, horizon)
  plan.append("Act: gọi Model Tool để dự báo giá.")
  trace.append(trace_step("Model Tool", "ok", started, f"{forecast['horizon']} phiên từ {forecast['as_of_date']}"))

  started = time.time()
  kg = kg_tool(question)
  plan.append("Act: gọi KG Tool để lấy quan hệ 2-hop.")
  trace.append(trace_step("KG Tool", "ok", started, f"{len(kg['facts'])} facts"))

  started = time.time()
  hits = rag_tool(question, as_of_date)
  plan.append("Act: gọi RAG Tool với bộ lọc date <= AS_OF_DATE.")
  trace.append(trace_step("RAG Tool", "ok", started, f"{len(hits)} chunks"))

  started = time.time()
  report = build_report(question, forecast, kg, hits)
  plan.append("Reason: hợp nhất Forecast + KG + RAG.")
  plan.append("Act: sinh báo cáo theo template, không dùng API key.")
  trace.append(trace_step("Report Generator", "ok", started, "template"))

  return {
    "plan": plan,
    "tool_calls": trace,
    "forecast": forecast,
    "kg_seeds": kg["seeds"],
    "kg_facts": kg["facts"],
    "rag_hits": hits,
    "report": report,
    "trace": trace,
    "disclaimer": DISCLAIMER,
  }


def model_info():
  df = load_prices()
  metrics = load_metrics()
  return {
    "status": "ok",
    "ticker": "AMZN",
    "as_of_date": AS_OF_DATE,
    "rows": int(len(df)),
    "start_date": df["Date"].min().strftime("%Y-%m-%d"),
    "end_date": df["Date"].max().strftime("%Y-%m-%d"),
    "model_type": "Forecast Tool demo: rolling log-return; LSTM/GRU training scaffold included",
    "features": ["log_return", "range_ratio", "log_volume_change", "ma5_ratio", "ma20_ratio", "volatility10", "rsi14"],
    "metrics": metrics,
    "note": "Không phải khuyến nghị đầu tư; thay Forecast Tool bằng model LSTM/GRU sau khi train_model.py sinh artifact thật."
  }


def main():
  try:
    payload = read_input()
    action = payload.get("action", "ask")
    if action == "model_info":
      output = model_info()
    elif action == "prices":
      output = price_series(payload.get("start"), payload.get("end"))
    elif action == "forecast":
      output = forecast_tool(payload.get("as_of_date") or AS_OF_DATE, payload.get("horizon", 5))
    elif action == "ask":
      output = ask_agent(payload)
    else:
      output = {"error": True, "message": "Hành động không hợp lệ."}
    print(json.dumps(output, ensure_ascii=False))
  except Exception as exc:
    print(json.dumps({"error": True, "message": str(exc), "disclaimer": DISCLAIMER}, ensure_ascii=False))


if __name__ == "__main__":
  main()
