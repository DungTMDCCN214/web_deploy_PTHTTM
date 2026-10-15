import csv
import json
import math
import os
import sys
import warnings
from collections import defaultdict, deque

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

import joblib
import pandas as pd

try:
  from sklearn.feature_extraction.text import TfidfVectorizer
  from sklearn.metrics.pairwise import cosine_similarity
except Exception:
  TfidfVectorizer = None
  cosine_similarity = None


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "ml_models", "diabetes", "diabetes_model.sav")
KG_PATH = os.path.join(SCRIPT_DIR, "kg_triples.csv")
DOCS_PATH = os.path.join(SCRIPT_DIR, "docs.json")

FEATURES = [
  "Pregnancies",
  "Glucose",
  "BloodPressure",
  "SkinThickness",
  "Insulin",
  "BMI",
  "DiabetesPedigreeFunction",
  "Age",
]

INPUT_KEYS = [
  "pregnancies",
  "glucose",
  "bloodPressure",
  "skinThickness",
  "insulin",
  "bmi",
  "diabetesPedigreeFunction",
  "age",
]

MEDIANS = {
  "pregnancies": 3.0,
  "glucose": 117.0,
  "bloodPressure": 72.0,
  "skinThickness": 29.0,
  "insulin": 125.0,
  "bmi": 32.4,
  "diabetesPedigreeFunction": 0.38,
  "age": 29.0,
}

RANGES = {
  "pregnancies": (0, 20, "Số lần mang thai"),
  "glucose": (0, 300, "Glucose"),
  "bloodPressure": (0, 200, "Huyết áp"),
  "skinThickness": (0, 100, "Độ dày da"),
  "insulin": (0, 1000, "Insulin"),
  "bmi": (0, 80, "BMI"),
  "diabetesPedigreeFunction": (0, 3, "Diabetes Pedigree Function"),
  "age": (1, 120, "Tuổi"),
}

MISSING_ZERO_KEYS = {"glucose", "bloodPressure", "skinThickness", "insulin", "bmi"}


def read_input():
  raw = sys.stdin.read()
  if not raw and len(sys.argv) > 1:
    raw = sys.argv[1]
  return json.loads(raw or "{}")


def load_model():
  return joblib.load(MODEL_PATH)


def load_triples():
  triples = []
  with open(KG_PATH, encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
      triples.append((row["subject"], row["relation"], row["object"]))
  return triples


def load_docs():
  with open(DOCS_PATH, encoding="utf-8") as f:
    return json.load(f)


def parse_values(payload):
  values = {}
  notes = []
  errors = []

  for key in INPUT_KEYS:
    raw = payload.get(key)
    try:
      value = float(raw)
    except (TypeError, ValueError):
      errors.append(f"{RANGES[key][2]} phải là số.")
      continue

    low, high, label = RANGES[key]
    if value < low or value > high:
      errors.append(f"{label} phải nằm trong khoảng {low} đến {high}.")
      continue

    if key in MISSING_ZERO_KEYS and value == 0:
      values[key] = MEDIANS[key]
      notes.append(f"{label} bằng 0 nên được thay bằng trung vị {MEDIANS[key]}.")
    else:
      values[key] = value

  if errors:
    raise ValueError(" ".join(errors))
  return values, notes


def predict(values):
  model = load_model()
  frame = pd.DataFrame([[
    values["pregnancies"],
    values["glucose"],
    values["bloodPressure"],
    values["skinThickness"],
    values["insulin"],
    values["bmi"],
    values["diabetesPedigreeFunction"],
    values["age"],
  ]], columns=FEATURES)

  pred = int(model.predict(frame)[0])
  if hasattr(model, "predict_proba"):
    prob = float(model.predict_proba(frame)[0][1])
  else:
    prob = 1.0 if pred == 1 else 0.0

  if prob < 0.35:
    risk = "thap"
  elif prob < 0.60:
    risk = "trung_binh"
  else:
    risk = "cao"
  return prob, risk, pred


def build_findings(values):
  findings = []
  if values["glucose"] >= 200:
    findings.append("Glucose rất cao (>= 200 mg/dL).")
  elif values["glucose"] >= 140:
    findings.append("Glucose ở vùng rối loạn dung nạp (140-199 mg/dL).")
  if values["bmi"] >= 30:
    findings.append("BMI ở mức béo phì (>= 30).")
  elif values["bmi"] >= 25:
    findings.append("BMI ở mức thừa cân (25-29.9).")
  if values["bloodPressure"] >= 90:
    findings.append("Huyết áp tâm trương cao (>= 90 mmHg).")
  if values["age"] >= 45:
    findings.append("Tuổi từ 45 trở lên, nên sàng lọc định kỳ.")
  if values["diabetesPedigreeFunction"] >= 0.8:
    findings.append("Chỉ số phả hệ tiểu đường cao, gợi ý yếu tố gia đình.")
  if values["pregnancies"] >= 5:
    findings.append("Số lần mang thai cao, là một yếu tố cần theo dõi.")
  if not findings:
    findings.append("Chưa ghi nhận chỉ số vượt ngưỡng nổi bật trong bộ luật demo.")
  return findings


def seed_entities(values):
  seeds = []
  if values["glucose"] >= 200:
    seeds.append("Glucose_High")
  elif values["glucose"] >= 140:
    seeds.append("Glucose_Impaired")
  if values["bmi"] >= 30:
    seeds.append("BMI_Obese")
  elif values["bmi"] >= 25:
    seeds.append("BMI_Overweight")
  if values["bloodPressure"] >= 90:
    seeds.append("BP_High")
  if values["age"] >= 45:
    seeds.append("Age_45plus")
  if values["diabetesPedigreeFunction"] >= 0.8:
    seeds.append("Family_History")
  if values["pregnancies"] >= 5:
    seeds.append("Many_Pregnancies")
  return seeds or ["Lifestyle_Change"]


def kg_facts_for(seeds):
  triples = load_triples()
  outgoing = defaultdict(list)
  for s, r, o in triples:
    outgoing[s].append((s, r, o))

  seen_nodes = set(seeds)
  seen_facts = set()
  facts = []
  q = deque((seed, 0) for seed in seeds)
  while q:
    node, depth = q.popleft()
    if depth >= 2:
      continue
    for fact in outgoing.get(node, []):
      if fact not in seen_facts:
        seen_facts.add(fact)
        facts.append(list(fact))
      target = fact[2]
      if target not in seen_nodes:
        seen_nodes.add(target)
        q.append((target, depth + 1))
  return facts[:16]


def fallback_score(query, text):
  q_terms = set(query.lower().split())
  t_terms = set(text.lower().split())
  if not q_terms or not t_terms:
    return 0.0
  return len(q_terms & t_terms) / math.sqrt(len(q_terms) * len(t_terms))


def retrieve_docs(query, top_k=3):
  docs = load_docs()
  if TfidfVectorizer and cosine_similarity:
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([d["text"] for d in docs])
    qv = vectorizer.transform([query])
    scores = cosine_similarity(qv, matrix)[0]
  else:
    scores = [fallback_score(query, d["text"]) for d in docs]

  ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:top_k]
  hits = []
  for idx, score in ranked:
    if float(score) <= 0.02:
      continue
    doc = docs[idx]
    hits.append({
      "id": doc["id"],
      "source": doc["source"],
      "page": doc["page"],
      "text": doc["text"],
      "score": round(float(score), 4),
    })
  return hits


def model_info():
  try:
    model = load_model()
    model_type = type(model).__name__
    n_features = int(getattr(model, "n_features_in_", 0) or 0)
    feature_names = [str(x) for x in getattr(model, "feature_names_in_", FEATURES)]
    params = getattr(model, "get_params", lambda: {})()
    n_estimators = params.get("n_estimators")
    return {
      "status": "ok",
      "model_type": model_type,
      "n_features": n_features,
      "feature_names": feature_names,
      "has_predict_proba": bool(hasattr(model, "predict_proba")),
      "n_estimators": n_estimators,
      "metrics": {
        "accuracy": 0.766,
        "auc": 0.82,
        "f1": 0.67,
        "recall": 0.67,
        "note": "Tạm dùng số tham khảo vì project hiện chưa có diabetes.csv để tính lại trên test split."
      }
    }
  except Exception as exc:
    return {"status": "error", "message": str(exc)}


def make_report(prob, risk, findings, facts, hits, notes):
  risk_text = {"thap": "thấp", "trung_binh": "trung bình", "cao": "cao"}[risk]
  evidence = "; ".join([f"{h['source']} trang {h['page']}" for h in hits]) or "Cơ sở tri thức không có đủ thông tin."
  action = {
    "thap": "Duy trì ăn uống lành mạnh, vận động đều và theo dõi định kỳ.",
    "trung_binh": "Nên điều chỉnh lối sống và cân nhắc kiểm tra đường huyết/HbA1c.",
    "cao": "Nên gặp bác sĩ hoặc cơ sở y tế để được đánh giá chính thức."
  }[risk]
  return {
    "prediction": f"Mô hình ước tính xác suất nguy cơ {prob * 100:.1f}%, mức {risk_text}.",
    "findings": " ".join(findings),
    "kg": " ".join([f"{s} {r} {o}." for s, r, o in facts[:5]]) or "Không có fact KG phù hợp.",
    "rag": evidence,
    "action": action,
    "preprocess_notes": notes,
    "disclaimer": "Kết quả chỉ phục vụ học tập; không thay thế chẩn đoán của bác sĩ."
  }


def analyze(payload):
  values, notes = parse_values(payload)
  prob, risk, pred = predict(values)
  findings = build_findings(values)
  seeds = seed_entities(values)
  facts = kg_facts_for(seeds)
  query = " ".join(findings + seeds + ["dinh duong van dong huyet ap insulin bien chung"])
  hits = retrieve_docs(query)
  report = make_report(prob, risk, findings, facts, hits, notes)
  return {
    "probability": round(prob, 4),
    "risk_level": risk,
    "prediction": pred,
    "inputs": values,
    "preprocess_notes": notes,
    "findings": findings,
    "kg_seeds": seeds,
    "kg_facts": facts,
    "rag_hits": hits,
    "report": report,
    "model_info": model_info(),
  }


def main():
  try:
    payload = read_input()
    if payload.get("action") == "model_info":
      output = model_info()
    else:
      output = analyze(payload)
    print(json.dumps(output, ensure_ascii=False))
  except Exception as exc:
    print(json.dumps({
      "error": True,
      "message": str(exc),
      "report": {
        "disclaimer": "Kết quả chỉ phục vụ học tập; không thay thế chẩn đoán của bác sĩ."
      }
    }, ensure_ascii=False))


if __name__ == "__main__":
  main()
